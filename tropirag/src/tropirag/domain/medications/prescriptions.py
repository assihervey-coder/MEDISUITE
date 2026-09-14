"""Représentation d'une prescription candidate (extraction, jamais posologie LLM)."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.domain.medications.entities import normalize_drug_name


@dataclass(slots=True)
class MedicationOrder:
    raw_name: str
    drug_code: str | None = None
    route: str | None = None
    frequency: str | None = None
    duration_days: float | None = None
    source: str = "clinician"      # clinician | ai_extraction

    @classmethod
    def from_dict(cls, d: dict) -> "MedicationOrder":
        raw = str(d.get("name", d.get("medication", "")))
        code = d.get("drug_code") or normalize_drug_name(raw)
        return cls(raw_name=raw, drug_code=code, route=d.get("route"),
                   frequency=d.get("frequency"), duration_days=d.get("duration_days"),
                   source=str(d.get("source", "clinician")))
