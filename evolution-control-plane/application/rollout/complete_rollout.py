"""Cas d'usage — complétion de rollout (RELEASED) + événement."""
from __future__ import annotations

from ...domain.proposal.events import RELEASE_COMPLETED, emit
from ...domain.rollout.stages import RolloutPlan


def complete_rollout(plan: RolloutPlan) -> dict:
    if not plan.finished:
        return {"completed": False, "reason": "stages non tous PASSÉS",
                "rollout": plan.to_dict()}
    emit(RELEASE_COMPLETED, release=plan.release_id)
    return {"completed": True, "release": plan.release_id,
            "next_state": "MONITORED"}
