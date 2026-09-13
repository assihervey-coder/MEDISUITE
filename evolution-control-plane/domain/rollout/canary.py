"""Canary — étapes de pourcentage et conditions de poursuite."""
from __future__ import annotations

from .feature_flags import PROGRESSION, FeatureFlag

CANARY_STEPS = ["CANARY", "P10", "P25", "P50", "P100"]


def canary_next(flag: FeatureFlag) -> FeatureFlag | None:
    """Étape canary suivante (None si sorti du tunnel canary ou terminé)."""
    if flag.state not in CANARY_STEPS:
        idx = PROGRESSION.index(flag.state)
        nxt = PROGRESSION[min(idx + 1, len(PROGRESSION) - 1)]
        return FeatureFlag(flag.key, nxt) if nxt in CANARY_STEPS else None
    idx = CANARY_STEPS.index(flag.state)
    if idx == len(CANARY_STEPS) - 1:
        return None
    return FeatureFlag(flag.key, CANARY_STEPS[idx + 1])
