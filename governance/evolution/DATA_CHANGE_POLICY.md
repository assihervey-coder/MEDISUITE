# DATA_CHANGE_POLICY

Stratégie **EXPAND → MIGRATE → VALIDATE → CONTRACT** — jamais de `DROP COLUMN`
direct en production.

- EXPAND : ajout additif compatible avec les lecteurs actuels.
- MIGRATE : backfill idempotent par lots, reprise sur incident.
- VALIDATE : double-lecture old/new + métriques de cohérence.
- CONTRACT : retrait après fenêtre de stabilité convenue (≥ 2 releases).

Classe plancher P5 (approbation maintainer + DPO). Toute migration embarque un
script de rollback (`migrations/rollback/`). Impact PHI : évaluation DPIA si
nouveau traitement de données de santé ; consentements RGPD intacts (révocables).
