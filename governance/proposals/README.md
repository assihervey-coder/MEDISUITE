# Propositions d'évolution

- `templates/` — 7 gabarits YAML (feature, architecture, ai, clinical, data, security, regulatory)
- `registry/proposals.yaml` — registre immuable par identifiant `PROP-XXXX`

Cycle : DRAFT → SUBMITTED → VALIDATED → CLASSIFIED → IMPACT_ANALYSIS → RISK_ASSESSMENT
→ DECISION_PENDING → (APPROVED | REJECTED | DEFERRED) → … → ACCEPTED.
Voir `../evolution/EVOLUTION_LIFECYCLE.md`.

Un dossier de proposition validée est **imuable** : toute correction = nouvelle version (`version: n+1`).
