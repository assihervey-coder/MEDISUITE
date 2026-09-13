"""CompatibilityReport — verdicts PASS/WARNING/REVIEW_REQUIRED/FAIL/NOT_APPLICABLE."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VERDICTS = ("PASS", "WARNING", "REVIEW_REQUIRED", "FAIL", "NOT_APPLICABLE")
ORDER = {"PASS": 0, "WARNING": 1, "REVIEW_REQUIRED": 2, "FAIL": 3, "NOT_APPLICABLE": -1}


@dataclass(slots=True)
class DimensionResult:
    dimension: str
    verdict: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict invalide : {self.verdict}")


@dataclass(slots=True)
class CompatibilityReport:
    change_set_id: str
    results: list[DimensionResult] = field(default_factory=list)

    def add(self, dimension: str, verdict: str, detail: str = "") -> None:
        self.results.append(DimensionResult(dimension, verdict, detail))

    def overall(self) -> str:
        """FAIL > REVIEW_REQUIRED > WARNING > PASS (NOT_APPLICABLE ignoré)."""
        active = [r.verdict for r in self.results if r.verdict != "NOT_APPLICABLE"]
        if not active:
            return "NOT_APPLICABLE"
        return max(active, key=lambda v: ORDER[v])

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_set_id": self.change_set_id,
            "compatibility": {r.dimension: r.verdict for r in self.results},
            "details": {r.dimension: r.detail for r in self.results if r.detail},
            "overall": self.overall(),
        }
