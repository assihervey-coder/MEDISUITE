# ADR-0008 — PostgreSQL base primaire, SQLite pour dev

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Chaque service avec sa propre BDD éviterait les jointures跨-domaines mais complique le dossier clinique unifié.

## Décision
PostgreSQL en prod (1 schéma par domaine), SQLite zéro-config en dev ; repositories isolés.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
