"""Cas d'usage — approbation avec quorum (matrice par classe)."""
from __future__ import annotations

from ...domain.decision.decision import QuorumNotMet, evaluate_quorum, required_roles
from ...domain.decision.entities import Approval


def approve(proposal_id: str, change_class: str, approvals: list[dict],
            author: str = "") -> dict:
    """approvals : [{role, actor}] — lève QuorumNotMet si insuffisant."""
    domain_approvals = [Approval(role=a["role"], actor=a["actor"]) for a in approvals]
    try:
        decision = evaluate_quorum(proposal_id, change_class, domain_approvals,
                                   author=author)
    except QuorumNotMet as exc:
        return {"approved": False, "reason": str(exc),
                "required_roles": required_roles(change_class)}
    return {**decision.to_dict(), "approved": True}
