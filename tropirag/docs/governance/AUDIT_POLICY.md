# Politique d'audit

Chaque réponse TropiRAG est traçable via :

- **Provenance** : règles appliquées (IDs + empreinte du référentiel),
  unités de preuve citées, modèles IA utilisés, décisions de gate.
- **AuditTrail JSONL** : runtime/logs/audit-YYYYMMDD.jsonl (append-only)
- **SQLite** : analyses historisées (tables cases, analyses, evidence_usage,
  audit_events)
- **Empreintes** : règles (fingerprint) + corpus (SHA-256 manifeste) —
  toute réponse indique SON état exact du référentiel.

## Conservation

- JSONL : 365 jours (rotation manuelle V1)
- Base locale : sous contrôle de l'établissement
- Aucune PII dans les logs (redaction : téléphone/email/IDs)
