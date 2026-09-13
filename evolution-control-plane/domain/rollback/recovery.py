"""Recovery — séquence de restauration ordonnée."""
from __future__ import annotations

RECOVERY_ORDER = (
    "feature_flag_state",      # 1. flags OFF d'abord (stopper l'exposition)
    "previous_version",        # 2. version logique précédente
    "database_checkpoint",     # 3. données
    "configuration_snapshot",  # 4. config
    "model_versions",          # 5. modèles
    "deployment_manifest",     # 6. manifeste
    "evidence_snapshot",       # 7. preuves
)


def recovery_plan(checkpoints_restored: list[str]) -> dict[str, list[str]]:
    missing = [c for c in RECOVERY_ORDER if c not in checkpoints_restored]
    return {"order": list(RECOVERY_ORDER), "restored": checkpoints_restored,
            "missing": missing}
