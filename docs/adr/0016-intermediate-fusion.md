# ADR-0016 — Fusion à niveau intermédiaire (embeddings)

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
La fusion tardive (vote) perd les interactions inter-modalités ; la fusion précoce exige des données alignées inexistantes.

## Décision
Fusion sur embeddings avec cross-attention : apprend les interactions sans alignement pixel-par-pixel.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
