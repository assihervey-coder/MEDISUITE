"""Cas d'usage — pause de rollout (gel conservatoire)."""
from __future__ import annotations

from ...domain.rollout.stages import RolloutPlan


def pause_rollout(plan: RolloutPlan, reason: str) -> dict:
    if not reason:
        raise ValueError("une pause doit être motivée")
    plan.pause()
    return {"paused": True, "reason": reason, "rollout": plan.to_dict()}
