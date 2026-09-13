# ADR-0019 — Apprentissage multi-tâches

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
6 têtes de sortie partagent les représentations → moins de données par tâche nécessaire.

## Décision
Têtes binary/multiclass/multilabel/regression/survival/segmentation sur un tronc partagé ; pertes pondérées par incertitude.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
