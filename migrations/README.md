# Migrations sûres

Stratégie **EXPAND → MIGRATE → VALIDATE → CONTRACT** (jamais de DROP direct en production).
- `database/expand/` — ajout additif (compat lecteurs existants)
- `database/migrate/` — backfill idempotent par lots
- `database/contract/` — retrait des anciennes colonnes après fenêtre de stabilité
- `rollback/` — scripts de retour arrière par migration (obligatoire)
