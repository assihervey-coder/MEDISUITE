# ADR-0015 — Explicabilité obligatoire en production

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Un score IA non explicable est inutilisable médicalement et opposable juridiquement.

## Décision
explainability-service (GradCAM, SHAP, LIME, attention viz, importance par modalité) : chaque inférence IA expose ses justifications.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
