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
- bandeau permanent « IA ≠ autorité clinique — la décision reste médicale ».

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

## 5. Tests

- TropiRAG : **358/358 pytest** (`cd tropirag && PYTHONPATH=src TROPIRAG_ROOT=$PWD python -m pytest tests`)
- Portail : vitest (logique `tropirag.ts` : payload, badges, déduplication),
  `tsc -b`, E2E navigateur (login → /decision → analyse → résultat complet).

## 6. Limites assumées (v0.5)

- Mesh IA en mode déterministe : la couche LLM (Ollama/vLLM) reste
  désactivée ; `TROPIRAG_INFERENCE_MODE` + `TROPIRAG_OLLAMA_URL` l'activent.
- Pas de TLS interne entre le portail et le service (réseau de dev) ;
  en production : reverse-proxy + `TROPIRAG_API_KEY`.
- L'ingestion du corpus (`make -C tropirag index`) est manuelle ; les
  snapshots d'index sont hors git (`tropirag/indexes/`).
