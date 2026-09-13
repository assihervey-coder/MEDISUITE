# Compatibilité

Matrice par dimension (API, DB, events, FHIR, DICOM, HL7, AI, clinical, configuration) :
`api/v1`, `api/v2`, … Chaque release candidate exécute `engines/compatibility-engine`
et produit un rapport PASS / WARNING / REVIEW_REQUIRED / FAIL dans `evidence/evolution/`.
