"""Cas d'usage — rejet motivé."""
from __future__ import annotations

from ...domain.decision.rejection import reject


def reject_proposal(proposal_id: str, actor: str, reason: str) -> dict:
    return reject(proposal_id, actor, reason)
