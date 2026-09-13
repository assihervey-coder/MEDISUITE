"""Stratégie de rollback — checkpoints requis avant tout déploiement."""
from __future__ import annotations

REQUIRED_CHECKPOINTS = (
    "previous_version", "database_checkpoint", "configuration_snapshot",
    "model_versions", "feature_flag_state", "deployment_manifest",
    "evidence_snapshot",
)


class CheckpointsIncomplete(Exception):
    pass


def assert_rollback_ready(present: set[str]) -> None:
    missing = [c for c in REQUIRED_CHECKPOINTS if c not in present]
    if missing:
        raise CheckpointsIncomplete(f"checkpoints manquants : {missing}")
