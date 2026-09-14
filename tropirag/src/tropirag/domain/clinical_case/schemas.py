"""Schémas API du cas clinique."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CaseRequest(BaseModel):
    """Requête d'analyse clinique (déterministe + IA encadrée)."""

    case_id: str | None = None
    patient: dict | None = None
    symptoms: list[dict] = Field(default_factory=list)
    symptom_codes: list[str] = Field(default_factory=list)
    free_text: str | None = None
    vitals: dict | None = None
    lab_results: list[dict] = Field(default_factory=list)
    travel: dict | None = None
    medications: list[dict] = Field(default_factory=list)
    consultation_date: str | None = None
    symptom_onset: str | None = None
    use_ai: bool = True
    language: str = "fr"


class CaseAnalysisResult(BaseModel):
    case_id: str
    urgency: str
    severity: str
    red_flags: list[dict] = Field(default_factory=list)
    escalations: list[dict] = Field(default_factory=list)
    differentials: list[dict] = Field(default_factory=list)
    required_tests: list[dict] = Field(default_factory=list)
    drug_constraints: list[dict] = Field(default_factory=list)
    evidence_summary: str = ""
    citations: list[dict] = Field(default_factory=list)
    narrative: str = ""
    ai_layers: list[str] = Field(default_factory=list)
    provenance: dict = Field(default_factory=dict)
    refusal: str | None = None
    disclaimer: str = ""
