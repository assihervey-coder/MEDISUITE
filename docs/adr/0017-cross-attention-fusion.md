# ADR-0017 — Cross-attention entre modalités

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
L'attention apprend quelles régions d'une modalité interrogent l'autre (ex : lésion IRM ↔ biomarqueur).

## Décision
CrossAttentionBlock Q/K/V multi-têtes, résiduel + LayerNorm, implémenté NumPy (réf) et PyTorch (v0.2).

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
