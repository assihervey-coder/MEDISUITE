"""Sélection de tests — consommateur direct du test-impact-engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class TestSelection:
    affected_tests: dict[str, int]   # {unit: 42, integration: 19, api: 8, ...}
    suites: list[str]                # chemins de suites à exécuter
    mandatory_full_regression: bool

    def to_dict(self) -> dict[str, Any]:
        return {"affected_tests": self.affected_tests,
                "suites": list(self.suites),
                "mandatory_full_regression": self.mandatory_full_regression}
