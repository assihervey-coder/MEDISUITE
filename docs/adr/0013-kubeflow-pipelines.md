# ADR-0013 — Kubeflow pour les pipelines d'entraînement

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
L'entraînement reproductible exige l'orchestration déclarative.

## Décision
Pipelines YAML par domaine (cancer, tumor, ..., multimodal) + Katib pour le tuning + KServe serving.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
