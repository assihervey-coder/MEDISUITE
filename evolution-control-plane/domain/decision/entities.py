"""Entité Decision + agrégats d'approbation/rejet."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class Approval:
    """Une approbation nominative par rôle (ISO 14155 : délégations tracées)."""

    role: str
    actor: str
    decided_at: str = field(default_factory=_now)
    comment: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "actor": self.actor,
                "decided_at": self.decided_at, "comment": self.comment}


@dataclass(slots=True)
class Rejection:
    reason: str
    actor: str
    decided_at: str = field(default_factory=_now)
    can_resubmit: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"reason": self.reason, "actor": self.actor,
                "decided_at": self.decided_at, "can_resubmit": self.can_resubmit}


@dataclass(slots=True)
class Decision:
    """Décision consolidée d'une proposition."""

    proposal_id: str
    outcome: str                       # APPROVED | REJECTED | DEFERRED
    approvals: list[Approval] = field(default_factory=list)
    rejection: Rejection | None = None
    conditions: list[str] = field(default_factory=list)
    evidence_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id, "outcome": self.outcome,
            "approvers": [a.to_dict() for a in self.approvals],
            "rejection": self.rejection.to_dict() if self.rejection else None,
            "conditions": list(self.conditions), "evidence_id": self.evidence_id,
        }
