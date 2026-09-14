"""Santé système consolidée."""
from __future__ import annotations

import time


def system_health(rules_count: int, evidence_units: int, mode: str) -> dict:
    return {
        "status": "ok",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "components": {
            "rule_engine": {"status": "ok", "rules": rules_count},
            "evidence_engine": {"status": "ok", "units": evidence_units},
            "ai_mesh": {"mode": mode},
        },
    }
