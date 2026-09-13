"""Cas d'usage — initiation d'un rollback (déclencheurs évalués)."""
from __future__ import annotations

from ...domain.proposal.events import ROLLBACK_TRIGGERED, emit
from ...domain.rollback.triggers import evaluate_triggers


def initiate_rollback(metrics: dict[str, float], alerts: list[str],
                      human_decision: bool = False) -> dict:
    triggers = evaluate_triggers(metrics, alerts, human_decision)
    if not triggers:
        return {"rollback_required": False, "triggers": []}
    trigger_names = [t.name for t in triggers]
    emit(ROLLBACK_TRIGGERED, triggers=trigger_names)
    return {"rollback_required": True, "triggers": trigger_names,
            "first_action": "feature_flags_to_OFF"}
