"""Adapter MiniCPM."""
from __future__ import annotations

from typing import Any


def parse_triage(structured: Any) -> dict:
    if not isinstance(structured, dict):
        return {"flag": "unknown", "confidence": None, "reason": "",
                "recommended_action": "", "parse_ok": False}
    return {"flag": str(structured.get("flag", "unknown")),
            "confidence": structured.get("confidence"),
            "reason": str(structured.get("reason", "")),
            "recommended_action": str(structured.get("recommended_action", "")),
            "parse_ok": True}
