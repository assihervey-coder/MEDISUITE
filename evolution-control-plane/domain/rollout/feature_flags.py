"""Feature flags — état par environnement, progression OFF→…→100 %."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[4]
DEFINITIONS = ROOT / "feature-flags" / "definitions" / "features.yaml"

PROGRESSION = ["OFF", "DEV", "STAGING", "PILOT", "CANARY", "P10", "P25", "P50", "P100"]


@dataclass(frozen=True, slots=True)
class FeatureFlag:
    key: str
    state: str = "OFF"

    def __post_init__(self) -> None:
        if self.state not in PROGRESSION:
            raise ValueError(f"état de flag invalide : {self.state}")


def promote(flag: FeatureFlag, steps: int = 1) -> FeatureFlag:
    idx = PROGRESSION.index(flag.state) + steps
    return FeatureFlag(flag.key, PROGRESSION[min(idx, len(PROGRESSION) - 1)])


def demote_to_off(flag: FeatureFlag) -> FeatureFlag:
    """Première action de rollback : tout à OFF."""
    return FeatureFlag(flag.key, "OFF")


def load_definitions() -> dict[str, Any]:
    if DEFINITIONS.exists():
        return yaml.safe_load(DEFINITIONS.read_text(encoding="utf-8")) or {}
    return {}
