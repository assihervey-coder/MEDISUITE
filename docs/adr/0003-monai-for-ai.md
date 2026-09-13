# ADR-0003 — MONAI pour l'imagerie médicale

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Réinventer les transforms 3D médicaux coûte des mois.

## Décision
Base d'entraînement MONAI+PyTorch (v0.2) ; la v0.1 livre une référence NumPy testable sans GPU.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
