"""Cas d'usage — plan de migration EXPAND → MIGRATE → VALIDATE → CONTRACT."""
from __future__ import annotations


def generate_migration_plan(columns: dict[str, list[str]]) -> dict:
    """columns : {table: [colonnes visées]} — jamais de DROP direct (P5)."""
    plan = {"strategy": "expand_migrate_contract", "phases": []}
    for table, cols in columns.items():
        plan["phases"].append({
            "table": table, "columns": cols,
            "expand": f"ALTER TABLE {table} ADD COLUMN *_new (nullable)",
            "migrate": f"backfill par lots idempotent ({table})",
            "validate": f"double-lecture old/new + métriques de cohérence ({table})",
            "contract": f"retrait ancien après fenêtre de stabilité ≥ 2 releases ({table})",
            "rollback": f"migrations/rollback/{table}.sql prêt AVANT exécution",
        })
    return plan
