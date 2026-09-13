"""Gates de rollout — bloquants avant chaque avancée."""
from __future__ import annotations

GATE_NAMES = ("smoke", "regression", "metric_slo", "clinical_signoff")


class GateFailed(Exception):
    pass


def check_gates(required: list[str], passed_gates: set[str]) -> None:
    missing = [g for g in required if g not in passed_gates]
    if missing:
        raise GateFailed(f"gates non franchis : {missing}")
