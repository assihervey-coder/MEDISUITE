"""Entité Assessment (dossier d'analyse consolidé) + dépôt."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .blast_radius import BlastRadius
from .impact import ImpactReport
from .risk import RiskScore


@dataclass(slots=True)
class Assessment:
    """Dossier d'évaluation rattaché à une proposition."""

    proposal_id: str
    impact: ImpactReport
    risk: RiskScore
    blast_radius: BlastRadius
    breaking_changes_detected: bool = False
    migration_required: bool = False
    complexity: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            **self.impact.to_dict(),
            **self.risk.to_dict(),
            **self.blast_radius.to_dict(),
            "breaking_changes_detected": self.breaking_changes_detected,
            "migration_required": self.migration_required,
            **self.complexity,
        }


class AssessmentRepository:
    """Dépôt JSON sur disque (un fichier par proposition)."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, assessment: Assessment) -> Path:
        p = self._root / f"{assessment.proposal_id}.assessment.json"
        p.write_text(json.dumps(assessment.to_dict(), indent=2, ensure_ascii=False),
                     encoding="utf-8")
        return p

    def get(self, proposal_id: str) -> dict[str, Any] | None:
        p = self._root / f"{proposal_id}.assessment.json"
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
