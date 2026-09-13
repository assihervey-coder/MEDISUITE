"""Cas d'usage — exécution du rollback (séquence de récupération ordonnée)."""
from __future__ import annotations

from ...domain.rollback.recovery import recovery_plan


def execute_rollback(rollback_id: str, release_id: str,
                     checkpoints_restored: list[str]) -> dict:
    plan = recovery_plan(checkpoints_restored)
    if plan["missing"]:
        return {"executed": False, "rollback_id": rollback_id,
                "missing_checkpoints": plan["missing"]}
    return {"executed": True, "rollback_id": rollback_id, "release": release_id,
            "restored_in_order": plan["order"], "next": "verify_rollback"}
