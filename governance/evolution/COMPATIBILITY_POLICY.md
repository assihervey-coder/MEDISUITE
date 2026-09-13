# COMPATIBILITY_POLICY

Aucune release candidate sans rapport du **compatibility-engine** couvrant :
API · base de données · événements · FHIR · DICOM · HL7 · contrats IA · contrats
cliniques · configuration.

Verdicts par dimension : PASS / WARNING / REVIEW_REQUIRED / FAIL / NOT_APPLICABLE.
Le verdict global agrège : un seul FAIL = release bloquée ; REVIEW_REQUIRED = gate
humaine ; WARNING = acceptable avec preuve justifiée dans le dossier.

Règles notables :
- API publique : breaking change → REVIEW_REQUIRED (jamais silencieux).
- Base de données : breaking → FAIL (stratégie expand/migrate/contract obligatoire).
- DICOM : changement de SOP class → FAIL.
- Clinique : TOUT changement → REVIEW_REQUIRED (même mineur).
- FHIR R6 eCRF : périmètre isolé (ADR-0024), pas de fuite vers R4 stable.
