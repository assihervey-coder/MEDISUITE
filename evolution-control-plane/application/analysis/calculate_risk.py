"""Cas d'usage — calcul de risque (config risk-levels.yaml)."""
from __future__ import annotations

from ...engines.risk_engine.engine import score


def calculate_risk(impacts: dict[str, str]) -> dict:
    return score(impacts)
