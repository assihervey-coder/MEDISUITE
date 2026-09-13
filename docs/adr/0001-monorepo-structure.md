# ADR-0001 — Monorepo unique

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Des équipes séparées par service créent de la duplication (modèles patient recopiés 5×).

## Décision
Un seul dépôt : services/, packages/, apps/, infrastructure/. Découplage par packages internes versionnés, pas par dépôts.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
