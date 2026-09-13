"""Rollout Engine — stratégie + plan de stages + gates + détection rollback."""
from __future__ import annotations

import importlib
from typing import Any

from ..._bridge import register

register()
_strategy = importlib.import_module("ecp.domain.rollout.strategy")
_stages = importlib.import_module("ecp.domain.rollout.stages")
_gates = importlib.import_module("ecp.domain.rollout.gates")
_triggers = importlib.import_module("ecp.domain.rollback.triggers")


def plan_release(release_id: str, change_class: str) -> dict[str, Any]:
    strat = _strategy.strategy_for(change_class)
    names: list[str] = []
    if strat.canary_steps:
        names = strat.targets + [f"canary-{p}%" for p in strat.canary_steps]
    else:
        names = strat.targets
    plan = _stages.RolloutPlan(release_id, names)
    return {"strategy": strat.to_dict(), "rollout": plan.to_dict(),
            "required_gates": strat.gates}


def gate_check(required_gates: list[str], passed: set[str]) -> dict[str, Any]:
    try:
        _gates.check_gates(required_gates, passed)
        return {"gates": "PASS", "passed": sorted(passed)}
    except _gates.GateFailed as exc:
        return {"gates": "FAIL", "detail": str(exc)}


def evaluate_rollback_conditions(metrics: dict[str, float],
                                 alerts: list[str],
                                 human_decision: bool = False) -> dict[str, Any]:
    triggered = _triggers.evaluate_triggers(metrics, alerts, human_decision)
    return {"rollback_required": bool(triggered),
            "triggers": [{"name": t.name, "detail": t.detail} for t in triggered]}
