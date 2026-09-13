# ADR-0007 — Compatibilité OpenELIS

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les laboratoires publics ivoiriens utilisent déjà OpenELIS.

## Décision
laboratory-service pilote OpenELIS via HL7 v2 et expose ses propres workflows en amont.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
