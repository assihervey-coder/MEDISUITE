"""Cas d'usage — vérification d'un change set (checksum + units)."""
from __future__ import annotations


def verify_change(change_set: dict) -> dict:
    """Un change set figé doit avoir checksum + au moins une unit vérifiable."""
    checks = {
        "frozen": bool(change_set.get("immutable")),
        "checksum_present": bool(change_set.get("checksum")),
        "has_units": bool(change_set.get("units")),
        "rollback_supported": bool(change_set.get("rollback_supported")),
    }
    return {"verified": all(checks.values()), "checks": checks}
