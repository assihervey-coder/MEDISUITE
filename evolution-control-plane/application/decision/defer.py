"""Cas d'usage — report avec condition de revisite."""
from __future__ import annotations

from ...domain.decision.rejection import defer


def defer_proposal(proposal_id: str, actor: str, reason: str, revisit: str) -> dict:
    return defer(proposal_id, actor, reason, revisit)
