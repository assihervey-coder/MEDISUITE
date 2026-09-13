# ADR-0001 (governance) — Evolution Control Plane V1

Statut : **ACCEPTÉE** · Date : 2026-09-14 · Proposant : maintainer
Correspond plateforme : `docs/adr/` (n° 0001-0026 inchangés)

## Contexte
MEDISUITE (39 services, 2 packages, 26 configs IA, 26 datasets, portal 96 écrans)
évolue vite ; chaque évolution doit être traçable au sens dispositif médical
(ISO 13485 §8, ISO 14971, IEC 62304 §8 gestion de configuration).

## Décision
Poser une **couche de gouvernance d'évolution** AU-DESSUS de la plateforme :
proposition → impact → risque → décision → change set → validation → release
contrôlée → monitoring → rollback/acceptation → preuve → nouvelle baseline.
V1 in-process (FastAPI + filesystem), API `/api/v1/evolution/*`, port 8400.

## Conséquences
- NO DIRECT CHANGE : toute évolution notable passe par une PROP-*.
- La baseline (`architecture/baseline/`) est dérivée des sources de vérité.
- Les moteurs (impact, risque, compatibilité, test-impact, rollout) consomment
  la baseline réelle — pas de documentation parallèle fantôme.
- V2 possible : stockage Postgres, bus d'événements Kafka, UI dédiée.
