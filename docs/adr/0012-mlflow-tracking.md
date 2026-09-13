# ADR-0012 — MLflow pour le tracking d'expériences

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les scores cliniques doivent être traçables par version de modèle.

## Décision
MLflow server dédié + model registry ; chaque prédiction en prod référence model_version.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
