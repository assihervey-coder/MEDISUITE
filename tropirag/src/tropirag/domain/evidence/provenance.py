"""Provenance : tracer chaque élément de la réponse jusqu'à sa source."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProvenanceRecord:
    """Un maillon de la chaîne de traçabilité d'une décision."""

    element: str          # 'rule:malaria-suspicion-001' | 'evidence:eu-...' | 'model:med42'
    kind: str             # rule | evidence | model | clinician | config
    detail: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProvenanceChain:
    records: list[ProvenanceRecord] = field(default_factory=list)

    def add(self, rec: ProvenanceRecord) -> None:
        self.records.append(rec)

    def rules_used(self) -> list[str]:
        return [r.element for r in self.records if r.kind == "rule"]

    def evidence_used(self) -> list[str]:
        return [r.element for r in self.records if r.kind == "evidence"]

    def models_used(self) -> list[str]:
        return [r.element for r in self.records if r.kind == "model"]

    def to_dict(self) -> dict:
        return {"records": [
            {"element": r.element, "kind": r.kind, "detail": r.detail} for r in self.records
        ]}
