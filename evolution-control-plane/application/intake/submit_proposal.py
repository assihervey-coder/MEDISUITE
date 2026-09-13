"""Cas d'usage — soumission d'une proposition (intake)."""
from __future__ import annotations

from typing import Any

from ...domain.proposal.entities import Proposal
from ...domain.proposal.enums import ImpactLevel, Outcome, ProposalState, ProposalType
from ...domain.proposal.repository import InMemoryProposalRepository
from ...domain.proposal.value_objects import ImpactVector, ProposalId


def submit(data: dict[str, Any], repo: InMemoryProposalRepository | None = None,
           proposal_id: str | None = None) -> Proposal:
    """Crée + soumet une proposition depuis un dict (YAML registry ou API)."""
    repo = repo or InMemoryProposalRepository()
    impacts = ImpactVector(
        clinical=ImpactLevel(data.get("clinical_impact", "NONE")),
        patient_safety=ImpactLevel(data.get("patient_safety_impact", "NONE")),
        security=ImpactLevel(data.get("security_impact", "NONE")),
        data=ImpactLevel(data.get("data_impact", "NONE")),
        api=ImpactLevel(data.get("api_impact", "NONE")),
        ai=ImpactLevel(data.get("ai_impact", "NONE")),
    )
    proposal = Proposal(
        id=ProposalId(proposal_id or repo.next_id().value),
        title=data.get("title", ""),
        type=ProposalType(data.get("type", "FEATURE")),
        requested_by=data.get("requested_by", "unknown"),
        affected_domains=list(data.get("affected_domains", [])),
        changed_paths=list(data.get("changed_paths", [])),
        breaking_change=bool(data.get("breaking_change", False)),
        impacts=impacts,
        migration_required=bool(data.get("migration_required", False)),
        human_approval_required=bool(data.get("human_approval_required", True)),
        rollback_required=bool(data.get("rollback_required", True)),
    )
    proposal.submit(data.get("requested_by", "unknown"))
    repo.save(proposal)
    return proposal
