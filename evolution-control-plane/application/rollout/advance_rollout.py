"""Cas d'usage — avancée de rollout (gates + SLO vérifiés)."""
from __future__ import annotations

from ...domain.rollout.monitoring import Metrics, SloEvaluator
from ...domain.rollout.stages import RolloutPlan
from ...domain.rollout.gates import check_gates, GateFailed


def advance_rollout(plan: RolloutPlan, passed_gates: set[str],
                    required_gates: list[str], metrics: Metrics | None = None) -> dict:
    check_gates(required_gates, passed_gates)
    if metrics is not None:
        ok, breaches = SloEvaluator().evaluate(metrics)
        if not ok:
            return {"advanced": False, "slo": "BREACH", "breaches": breaches,
                    "recommended_action": "PAUSE_OR_ROLLBACK"}
    stage = plan.advance()
    if stage is None:
        return {"advanced": True, "finished": plan.finished,
                "rollout": plan.to_dict()}
    return {"advanced": True, "finished": plan.finished,
            "current_stage": stage.name, "rollout": plan.to_dict()}
