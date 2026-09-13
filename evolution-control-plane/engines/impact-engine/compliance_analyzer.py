"""Analyseur conformité — dossiers MDR/SMQ/submissions touchés."""
from __future__ import annotations

MDR_MAP = {
    "technical-documentation": "TD",
    "model-cards": "MC",
    "clinical": "CLIN",
    "submissions": "SUB",
}


def analyze_compliance(changed_paths: list[str]) -> dict:
    touched = [p for p in changed_paths if p.startswith("compliance/")]
    kinds = sorted({MDR_MAP.get(part, part) for p in touched
                    for part in p.split("/")[2:3]})
    return {"compliance_paths": touched, "dossier_kinds": kinds, "count": len(touched)}
