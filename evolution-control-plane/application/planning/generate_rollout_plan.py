"""Cas d'usage — plan de rollout (stratégie + stages + gates par classe)."""
from __future__ import annotations

from ...engines.rollout_engine.engine import plan_release


def generate_rollout_plan(release_id: str, change_class: str) -> dict:
    return plan_release(release_id, change_class)
