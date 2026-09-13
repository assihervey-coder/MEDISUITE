# ADR-0002 — DICOMweb (QIDO-RS/WADO-RS/STOW-RS)

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les API DICOM propriétaires verrouillent les intégrations visualiseurs.

## Décision
Endpoints DICOMweb conformes PS3.18 dans imaging-service + dicom-gateway ; Orthanc comme PACS de référence.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
