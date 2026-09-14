"""Schéma API de réponse — miroir de ClinicalResponse (dict sérialisé)."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CaseResponseOut(BaseModel):
    case_id: str
    urgency: str
    severity: str
    narrative: str = ""
    differentials: list[dict] = Field(default_factory=list)
    red_flags: list[dict] = Field(default_factory=list)
    escalations: list[dict] = Field(default_factory=list)
    required_tests: list[dict] = Field(default_factory=list)
    drug_constraints: list[dict] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)
    ai_layer: str = "deterministic"
    ai_synthesis: str | None = None
    refusal: str | None = None
    disclaimer: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)
