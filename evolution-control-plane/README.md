# MEDISUITE Evolution Control Plane V1

Couche de **gouvernance d'évolution** posée AU-DESSUS de MEDISUITE (jamais à la place).
Tout changement passe par le cycle :

`PROPOSITION → IMPACT → RISQUE → DÉCISION → CHANGE SET → VALIDATION → APPROBATION
→ RELEASE CONTRÔLÉE → MONITORING → (ROLLBACK | ACCEPTATION) → NOUVELLE BASELINE`

## Règle absolue V1
**NO DIRECT CHANGE** — aucune modification des services de production sans proposition
enregistrée, impact analysé, décision tracée.

## Layout
- `config/` — politiques machine (risque, classification, matrice d'approbation, rollout, rollback, compatibilité)
- `domain/` — modèle du domaine (proposal, assessment, decision, change, compatibility, validation, rollout, rollback)
- `engines/` — moteurs d'analyse (impact, risk, compatibility, test-impact, rollout)
- `application/` — cas d'usage (intake → analysis → decision → planning → implementation → validation → rollout/rollback)
- `adapters/` — adaptateurs techniques (filesystem, git, github, ci, k8s, fhir, notification)
- `services/` — faïades de service (13 services logiques, in-process en V1)
- `workflows/` — pipelines déclaratifs YAML
- `api/` — REST `/api/v1/evolution/*` (FastAPI) + schémas + événements
- `tests/` — verrous pytest

## Lancement
```bash
uvicorn evolution-control-plane.api.rest.app:app --port 8400
# docs : http://localhost:8400/docs
```

## Position architecturale
```
EVOLUTION CONTROL PLANE V1  (decide / analyse / control)
        │  controlled changes
        ▼
MEDISUITE EXISTANT (39 services — patient/clinical/AI/imaging/lab/…)
```
