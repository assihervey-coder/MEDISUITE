# Intégration TropiRAG — aide à la décision clinique (v0.5)

> TropiRAG V1.4 (« Compagnon clinique de terrain — fièvre + voyage, Afrique de
> l'Ouest ») est intégré au monorepo MEDISUITE sous `tropirag/` et exposé comme
> **40ᵉ microservice** : `tropirag-service` (:8304). Conformité ADR 0001
> (microservices), ADR 0013 (autorité clinique déterministe) et la règle
> fondatrice de TropiRAG : **IA ≠ autorité clinique**.

## 1. Architecture

```
apps/web-portal  →  /api/tropirag/api/v1/...  (proxy Vite, préfixe retiré)
        │
        ▼
tropirag-service :8304  (tropirag.api.app:app — API FastAPI TropiRAG)
        │
        ├── clinical_engine   170 règles YAML déterministes (rule engine)
        ├── safety            safety gate, refus, médication, PII
        ├── evidence_engine   RAG : 47 unités de preuve OMS/CDC/MSF, BM25 + vecteurs
        └── persistence       SQLite (data/tropirag.db), audit JSONL
```

- Le moteur est vendu **tel quel** (`tropirag/`, licence propriétaire) : aucun
  fork du code, l'ajout MEDISUITE est limité au registry, au proxy et à l'UI.
- Le mesh IA fonctionne en mode **déterministe** par défaut (aucun appel
  externe) — cohérent avec l'exigence offline-first et la politique « local
  LLM uniquement » de TropiRAG.
- Le portail appelle le service avec la convention gateway classique
  (`/api/{service}/api/v1/...`), le proxy retire le préfixe.

## 2. Lancement

```bash
PYTHONPATH=. python services/run_all.py --up --only tropirag-service
# Health : http://localhost:8304/api/v1/health
# Dashboard natif TropiRAG : http://localhost:8304/  (web + /mobile PWA)
```

Le service est enregistré dans `services/registry.py` (group « gateway »,
`health_path: /api/v1/health`, env `TROPIRAG_ROOT` / `TROPIRAG_DB_PATH`
injectés par `run_all.py`). En production, définir `TROPIRAG_API_KEY`
(l'auth middleware TropiRAG s'active dès que la clé est non vide) et router
via l'api-gateway.

## 2 bis. Mesh LLM local — activation (`TROPIRAG_OLLAMA_URL`)

```bash
# Mono-commande : nœud Ollama réel si binaire présent, sinon nœud SIMULÉ
# embarqué (tropirag/scripts/mock_ollama_server.py — réponses déterministes
# ancrées sur les preuves du prompt, aucun contenu clinique inventé),
# puis redémarrage de tropirag-service en mode mesh :
scripts/dev/start_ollama_mesh.sh            # port 11434 par défaut

# Équivalent manuel (nœuds réels, multi-nœuds éventuel) :
export TROPIRAG_INFERENCE_MODE=ollama
export TROPIRAG_OLLAMA_URL=http://127.0.0.1:11434      # nœud unique
# export TROPIRAG_OLLAMA_NODES=text=http://node1:11434,vision=http://node1:11434
PYTHONPATH=. python services/run_all.py --up --only tropirag-service
```

- `GET /api/v1/inference/nodes` : topologie réelle (joignabilité, version,
  modèles, latence, pulls manquants) — consommé par le badge du portail.
- Mode mesh actif : `POST /api/v1/cases` accepte `use_ai: true` → synthèse
  Med42 **auditée par le Safety Gate** (couverture de preuves, détection
  d'hallucinations) ; refus possible, repli déterministe automatique.
- Retour au mode sûr : `TROPIRAG_INFERENCE_MODE=deterministic` (badge UI
  « IA déterministe hors-ligne »).
- `services/registry.py` expose ces variables (surchargeables à chaud avant
  `run_all.py --up`) — valeurs par défaut : `deterministic` +
  `http://127.0.0.1:11434`.

## 3. Écran portail — 🧭 Aide à la décision (`/decision`)

`src/features/decision/TropiRagConsult.tsx` :

- formulaire patient (âge, sexe, grossesse), constantes (température),
  symptômes en chips (taxonomie live `/api/v1/symptoms/taxonomy`, repli local),
  expositions (pays, rural, forêt, eaux stagnantes, jours de retour), TDR
  paludisme, contexte libre ;
- POST `/api/v1/cases` → urgence (routine → danger vital), gravité, red flags,
  escalades, différentiels pondérés, examens requis (dédupliqués),
  contraintes médicamenteuses, narrative, **citations sourcées** [n] avec
  extraits, refus moteur et disclaimer ;
- bandeau permanent « IA ≠ autorité clinique — la décision reste médicale » ;
- **badge mesh LLM** (état `GET /api/v1/inference/nodes`) : « Mesh LLM local
  actif (n nœuds) » / « nœud injoignable (repli déterministe) » / « IA
  déterministe hors-ligne » ;
- case **« Synthèse IA du mesh (auditée) »** (visible uniquement si un nœud
  est joignable) → `use_ai: true` ; la synthèse s'affiche séparément de la
  synthèse déterministe, estampillée « auditée par le Safety Gate ».

## 4. Cas de test de bout en bout

Femme 28 ans, enceinte, fièvre + céphalées + vomissements, 39,2 °C, séjour
rural CI, TDR palu positif →

| Sortie | Valeur |
|---|---|
| Urgence / gravité | `emergency` / `severe` |
| Différentiels | malaria 100 %, dengue 40 % |
| Red flag | paludisme gestationnel urgent |
| Contre-indications | primaquine, doxycycline, AINS (dengue)… |
| Citations | 5 unités de preuve (OMS ×4, national ×1) |

## 6. Surveillance des éclosions → écran Épidémiologie

- Source : `GET /api/v1/surveillance/map?days=30` (OutbreakMonitor TropiRAG)
  — agrégation **100 % déterministe** des analyses persistées par district
  sanitaire CI (résolu depuis le segment de voyage), comptes identiques à
  l'export DHIS2 ; signal = dernière semaine ≥ précédente + 2 et ≥ 3 cas.
- Portail (`src/features/epidemiology/`) : carte schématique des **14
  districts** (grille géographique, intensité = densité de cas, cerclage
  rouge ⚠ sur les districts en signal), liste des signaux (S38 vs S37,
  suspect principal), puces nationales par maladie, compartiment « non
  localisés », lien croisé vers `/decision`. Échec en mode dégradé : la
  carte est indépendante des indicateurs analytics.
- Jeu de démo reproductible (analyses réelles du rule engine, antidatées
  sur 3 semaines) : `scripts/dev/seed_tropirag_surveillance.py`
  (idempotent — manifeste `data/tropirag-surv-seed.json`).

## 7. Tests

- TropiRAG : **358/358 pytest** (`cd tropirag && PYTHONPATH=src TROPIRAG_ROOT=$PWD python -m pytest tests`)
- Portail : vitest (logique `tropirag.ts` : payload, badges, déduplication,
  mesh ; `outbreaks.ts` : carte, signaux, libellés), `tsc -b`, E2E navigateur
  (login → /decision avec badge mesh + synthèse IA → /epidemiologie carte
  des éclosions).

## 8. Limites assumées (v0.5)

- En mode déterministe pur, la couche LLM reste désactivée ; l'activation
  se fait via `TROPIRAG_INFERENCE_MODE` + `TROPIRAG_OLLAMA_URL`
  (cf. § 2 bis) — en sandbox sans GPU, le nœud simulé embarqué joue le
  rôle du mesh sans inventer de contenu clinique.
- Pas de TLS interne entre le portail et le service (réseau de dev) ;
  en production : reverse-proxy + `TROPIRAG_API_KEY`.
- L'ingestion du corpus (`make -C tropirag index`) est manuelle ; les
  snapshots d'index sont hors git (`tropirag/indexes/`).
