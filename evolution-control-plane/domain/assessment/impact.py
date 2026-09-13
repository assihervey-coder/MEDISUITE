"""Impact — rapport d'impact structurel d'une proposition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ImpactReport:
    """Comptage des surfaces touchées (dérivera de la baseline + chemins modifiés)."""

    files: int = 0
    services: int = 0
    databases: int = 0
    apis: int = 0
    events: int = 0
    ai_models: int = 0
    clinical_rules: int = 0
    tests: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    def total(self) -> int:
        return (self.files + self.services + self.databases + self.apis +
                self.events + self.ai_models + self.clinical_rules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "impact": {
                "files": self.files, "services": self.services,
                "databases": self.databases, "apis": self.apis,
                "events": self.events, "ai_models": self.ai_models,
                "clinical_rules": self.clinical_rules, "tests": self.tests,
            },
            "details": self.details,
        }
