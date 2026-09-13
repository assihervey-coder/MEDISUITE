# ADR-0014 — Apprentissage fédéré inter-établissements

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les données patients ne peuvent pas sortir des établissements (RGPD art. 44).

## Décision
Flower/NVFlare en option ; gradient aggregation sans partage de données brutes.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
