"""Commandes du domaine (intention explicite, immuables)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .enums import ImpactLevel, ProposalType
from .value_objects import ProposalId


@dataclass(frozen=True, slots=True)
class SubmitProposal:
    id: ProposalId
    title: str
    proposal_type: ProposalType
    requested_by: str
    affected_domains: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    breaking_change: bool = False
    clinical_impact: ImpactLevel = ImpactLevel.NONE
    patient_safety_impact: ImpactLevel = ImpactLevel.NONE
    security_impact: ImpactLevel = ImpactLevel.NONE
    data_impact: ImpactLevel = ImpactLevel.NONE
    api_impact: ImpactLevel = ImpactLevel.NONE
    ai_impact: ImpactLevel = ImpactLevel.NONE
    migration_required: bool = False


@dataclass(frozen=True, slots=True)
class AnalyzeProposal:
    proposal_id: ProposalId


@dataclass(frozen=True, slots=True)
class DecideProposal:
    proposal_id: ProposalId
    actor: str
    reason: str
