"""Cas d'usage — démarrage d'un rollout (checkpoints + gates requis)."""
from __future__ import annotations

from ...domain.rollback.checkpoints import CheckpointSet
from ...domain.rollback.strategy import CheckpointsIncomplete, assert_rollback_ready
from ...engines.rollout_engine.engine import plan_release


def start_rollout(release_id: str, change_class: str,
                  checkpoints: dict[str, str]) -> dict:
    cp = CheckpointSet(release_id=release_id)
    for name, ref in checkpoints.items():
        cp.add(name, ref)
    assert_rollback_ready(cp.present)  # lève CheckpointsIncomplete si trou
    plan = plan_release(release_id, change_class)
    return {"started": True, **plan, "checkpoints": cp.to_dict()}
