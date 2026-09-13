# ADR-0005 — FHIR R4 comme langage d'échange clinique

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les schémas propriétaires empêchent l'interconnexion HIS existants.

## Décision
integration-service expose FHIR R4 (Patient, Observation, Condition, Encounter) ; HL7v2 via passerelle MLLP.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
