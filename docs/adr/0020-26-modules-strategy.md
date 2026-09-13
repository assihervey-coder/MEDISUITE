# ADR-0020 — Stratégie des 26 modules de spécialités

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Dupliquer 26× le même squelette produit 26 dette techniques.

## Décision
Un générateur (tools/generators/specialty-generator) + un noyau partagé (clinical-rules) : chaque module n'écrit QUE sa logique distinctive.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
