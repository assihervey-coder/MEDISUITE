# Contrats versionnés

- `evolution/` — JSON Schema des 7 artefacts du control plane (proposal, assessment, decision, change, validation, rollout, rollback)
- `api/`, `events/`, `clinical/`, `ai/`, `fhir/`, `dicom/`, `hl7/` — contrats d'interface vérifiés par le compatibility-engine avant toute release

Un contrat changeant = proposition de classe P4+ (voir `governance/evolution/CHANGE_CLASSIFICATION.md`).
