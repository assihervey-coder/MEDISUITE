# ADR-0006 — Orthanc comme PACS open-source

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Un PACS commercial coûte 50-150 k€/an et bride l'autonomie.

## Décision
Orthanc par défaut, connecteurs dcm4chee et PACS commerciaux conservés via pacs_connector.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
