"""Cas d'usage — validation de complétude d'une proposition."""
from __future__ import annotations

from typing import Any

from ...domain.proposal.entities import Proposal
from ...domain.proposal.enums import ProposalState


REQUIRED_FIELDS = ("title", "type", "requested_by", "affected_domains")


def validate(proposal: Proposal) -> dict[str, Any]:
    """VALIDATED si les champs obligatoires sont présents et cohérents."""
    errors: list[str] = []
    if len(proposal.title) < 5:
        errors.append("titre trop court (≥ 5 caractères)")
    if not proposal.affected_domains:
        errors.append("affected_domains vide")
    if not proposal.requested_by or proposal.requested_by == "unknown":
        errors.append("requested_by requis")
    if proposal.migration_required and not proposal.rollback_required:
        errors.append("migration sans rollback interdit (DATA_CHANGE_POLICY)")
    if proposal.impacts.patient_safety.value == "HIGH" and \
            not proposal.human_approval_required:
        errors.append("impact sécurité patient HIGH exige approbation humaine")
    if errors:
        return {"valid": False, "errors": errors}
    if proposal.status.value == "SUBMITTED":
        proposal.transition(ProposalState.VALIDATED, "intake", "complétude vérifiée")
    return {"valid": True, "errors": []}
