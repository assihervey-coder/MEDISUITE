"""Complexité — estimation de l'effort de mise en œuvre (P1 facile → P9 lourd)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FACTORS = {
    "docs_only": -2, "single_service": 0, "multi_service": 2,
    "migration": 3, "model_training": 4, "clinical_validation": 4,
    "breaking": 3, "regulatory": 3,
}


@dataclass(frozen=True, slots=True)
class Complexity:
    points: int
    band: str  # TRIVIAL | SIMPLE | MODERE | LOURD | MINEUR_TERAIN

    def to_dict(self) -> dict[str, Any]:
        return {"complexity": {"points": self.points, "band": self.band}}


def compute_complexity(flags: dict[str, bool]) -> Complexity:
    pts = sum(v for k, v in FACTORS.items() if flags.get(k))
    band = ("TRIVIAL" if pts <= 0 else "SIMPLE" if pts <= 2 else
            "MODERE" if pts <= 5 else "LOURD" if pts <= 9 else "MAJEUR")
    return Complexity(points=max(pts, 0), band=band)
