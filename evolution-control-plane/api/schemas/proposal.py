"""Schémas Pydantic — proposition (arbre conforme)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProposalIn(BaseModel):
    title: str = Field(min_length=5)
    type: str = "FEATURE"
    requested_by: str = "unknown"
    affected_domains: list[str] = []
    changed_paths: list[str] = []
    breaking_change: bool = False
    clinical_impact: str = "NONE"
    patient_safety_impact: str = "NONE"
    security_impact: str = "NONE"
    data_impact: str = "NONE"
    api_impact: str = "NONE"
    ai_impact: str = "NONE"
    migration_required: bool = False


class DecisionIn(BaseModel):
    outcome: str  # APPROVED | REJECTED | DEFERRED
    actor: str
    reason: str = ""
    approvals: list[dict] = []
