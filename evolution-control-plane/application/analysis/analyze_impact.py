"""Cas d'usage — analyse d'impact via l'impact-engine."""
from __future__ import annotations

from ...engines.impact_engine.engine import analyze


def analyze_impact(changed_paths: list[str]) -> dict:
    result = analyze(changed_paths)
    return {**result.counts(), "components": result.components,
            "details": {k: v for k, v in result.details.items()
                        if k in ("security", "compliance", "clinical", "ai")}}
