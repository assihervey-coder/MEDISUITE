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

## 2 bis. Mesh LLM local — mono-nœud (`TROPIRAG_OLLAMA_URL`) et multi-nœuds GPU (`TROPIRAG_OLLAMA_NODES`)

```bash
# Mono-commande : nœud Ollama réel si binaire présent, sinon nœud SIMULÉ
# embarqué (tropirag/scripts/mock_ollama_server.py — réponses déterministes
# ancrées sur les preuves du prompt, aucun contenu clinique inventé),
# puis redémarrage de tropirag-service en mode mesh :
scripts/dev/start_ollama_mesh.sh            # mono-nœud, port 11434 par défaut

# MULTI-NŒUDS GPU — topologie tropirag/deployment/ollama/nodes.yaml (4 nœuds) :
scripts/dev/start_ollama_mesh.sh --multi
#   node1 :11434 input-evidence (speech/vision/embeddings/reranking)
#   node2 :11435 reasoning-a    (text : med42-v2-70b, openbiollm-70b)
#   node3 :11436 reasoning-b    (réplique de node2 — domaine de panne distinct)
#   node4 :11437 audit-standby  (deepseek-r1-distill-32b)
# Avec le binaire ollama : un serveur ollama réel par nœud (OLLAMA_HOST/OLLAMA_MODELS
# dédiés) ; sinon n nœuds simulés avec les sous-ensembles de modèles par rôle.

# Équivalent manuel (nœuds GPU réels, DNS interne) :
export TROPIRAG_INFERENCE_MODE=ollama
export TROPIRAG_OLLAMA_URL=http://node2:11434                      # nœud texte par défaut
export TROPIRAG_OLLAMA_NODES="speech=http://node1:11434,vision=http://node1:11434,\
embeddings=http://node1:11434,reranking=http://node1:11434,text=http://node2:11434,\
replicas=http://node3:11434|http://node4:11434"
PYTHONPATH=. python services/run_all.py --up --only tropirag-service
```

- **Routage par famille** (`OllamaGateway`) : modèle → famille (registre) →
  nœud ; ordre de repli déterministe famille → défaut → **répliques**
  (`replicas=URL|URL` ou `replica=` répétable) — si node2 tombe, la synthèse
  textuelle bascule sur node3 sans intervention.
- `GET /api/v1/inference/nodes` : topologie réelle (joignabilité par nœud,
  version, modèles, latence, routage familles, répliques, pulls manquants) —
  consommé par le badge du portail (« Mesh LLM local actif (4 nœuds) »).
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

## 6 bis. DHIS2 réel — export de la surveillance (MSP-CI)

La surveillance est branchée sur le système national DHIS2 (V1.3 TropiRAG) :

- **API** : `POST /api/v1/export/dhis2` (agrège une semaine ISO en
  dataValueSets — 19 indicateurs mappés sur le dictionnaire MSP-CI,
  `configs/integrations/dhis2.yaml`), `GET .../status` (file + config),
  `POST .../push` (envoi explicite de la file). Formats : JSON, CSV, ADX 2.0.
- **Sécurité** : mode `offline_queue` par défaut — aucun envoi réseau
  implicite ; le push est un acte explicite (utilisateur ou cron MSP-CI).
- **Portail** (écran Épidémiologie, panneau « Export DHIS2 ») : statut
  (mode, org unit, file en attente/envoyés/échecs), export de la semaine
  ISO courante ou saisie (`2026W38`), chips d'indicateurs agrégés, aperçu
  du payload dataValueSets, bouton push.
- **Serveur réel** (MSP-CI) via variables d'environnement (exposées par
  `services/registry.py`, surchargeables à chaud) :
  `TROPIRAG_DHIS2_MODE=push` + `TROPIRAG_DHIS2_BASE_URL` +
  `TROPIRAG_DHIS2_USERNAME` + `TROPIRAG_DHIS2_PASSWORD` (jamais en clair
  dans la config). Sans serveur : la file accumule, l'UI reste fonctionnelle.
- **Cron hebdomadaire automatique** (`TROPIRAG_DHIS2_AUTO`) : chaque lundi
  à 06:00 UTC (réglable : `TROPIRAG_DHIS2_PUSH_DAY`, `TROPIRAG_DHIS2_PUSH_HOUR_UTC`),
  le service exporte la semaine **écoulée** et :
  - `off` (défaut) : rien d'automatique — push manuel uniquement ;
  - `queue` : export en file, aucun appel réseau ;
  - `push` : export + envoi au serveur configuré (payload conservé en file
    si le transport est indisponible — rien n'est perdu).
  État persisté (`runtime/state/dhis2_cron.json`), exposé par
  `GET /api/v1/export/dhis2/cron` (affiché dans le panneau UI) et
  déclenchable à la main : `POST /api/v1/export/dhis2/cron/run`.
- **Répétition générale** : `scripts/dev/mock_dhis2_server.py` (port 11440)
  simule le serveur national — validation E2E complète effectuée :
  export 2026W38 (25 analyses → 7 valeurs) → file → push HTTP 200
  (`imported: 7, ignored: 0`) → file marquée « sent » ; cycle cron manuel
  2026W37 → 4 valeurs → push auto OK.
- **Prérequis au passage en production** : recopier les UIDs officiels du
  dictionnaire DHIS2 du Ministère dans `dhis2.yaml` (remplacer les
  placeholders `DE-TRPG-*` / `OU-TRPG-*`), puis `python
  tropirag/scripts/validate_dhis2_uids.py` — le validateur bloque le mode
  push tant que des placeholders subsistent.

## 7. Tests

- TropiRAG : **376/376 pytest** (`cd tropirag && PYTHONPATH=src TROPIRAG_ROOT=$PWD python -m pytest tests`) — dont réplicas multi-nœuds (routage,
  repli sur réplique), surcharges env DHIS2 (push, mdp jamais en clair) et
  cron hebdo (créneaux, semaine écoulée, mode queue sans réseau, échec
  propre sans serveur, état persisté).
- Noyau + services : **62/62** tests noyau, **39/39** suites services —
  correctif auth : jeton expiré/falsifié → **401** (le portail déconnecte)
  au lieu d'un faux 403 « permission requise » ; anonyme sans jeton → 403
  fail-closed inchangé ; Authorization relayé par l'api-gateway (les
  services revalident — source de vérité unique), X-User-* client purgés.
- Portail : vitest **90/90** (logique `tropirag.ts` : payload, badges,
  déduplication, mesh ; `outbreaks.ts` : carte, signaux, libellés ;
  `dhis2.ts` : semaine ISO, badges, file, cron, synthèse export), `tsc -b`,
  E2E navigateur (login → /decision badge « 4 nœuds » + synthèse IA →
  /epidemiologie carte des éclosions + panneau DHIS2 export→push→cron →
  /study promoteur sans faux 403).

## 8. Limites assumées (v0.5)

- En mode déterministe pur, la couche LLM reste désactivée ; l'activation
  se fait via `TROPIRAG_INFERENCE_MODE` + `TROPIRAG_OLLAMA_URL`/
  `TROPIRAG_OLLAMA_NODES` (cf. § 2 bis) — en sandbox sans GPU, les nœuds
  simulés embarqués jouent le rôle du mesh sans inventer de contenu
  clinique ; le jour du montage GPU réel, `--multi` avec le binaire ollama
  reproduit la même topologie.
- DHIS2 : UIDs placeholders tant que le MSP-CI n'a pas confirmé le
  dictionnaire national (§ 6 bis) ; le push réel est testé contre le
  récepteur de répétition, pas contre le serveur de production.
- Pas de TLS interne entre le portail et le service (réseau de dev) ;
  en production : reverse-proxy + `TROPIRAG_API_KEY`.
- L'ingestion du corpus (`make -C tropirag index`) est manuelle ; les
  snapshots d'index sont hors git (`tropirag/indexes/`).
