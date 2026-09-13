# ADR-0018 — Tolérance aux modalités manquantes

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
En Afrique de l'Ouest, 30-60 % des dossiers n'ont pas toutes les modalités ; un modèle exigeant toutes les modalités est inutilisable.

## Décision
Masquage + token de présence + dropout de modalités à l'entraînement ; l'inférence dégrade élégamment (jamais d'erreur, indicateur de confiance ajusté).

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
