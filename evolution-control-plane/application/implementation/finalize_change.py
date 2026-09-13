"""Cas d'usage — finalisation d'implémentation (IMPLEMENTATION terminée)."""
from __future__ import annotations


def finalize_change(change_set: dict, verification: dict) -> dict:
    if not verification.get("verified"):
        return {"finalized": False, "reason": "vérification incomplète"}
    return {"finalized": True, "change_set": change_set.get("id"),
            "proposal": change_set.get("proposal"),
            "next_state": "TECHNICAL_VALIDATION"}
