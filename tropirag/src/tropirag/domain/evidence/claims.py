"""Affirmations (claims) extraites d'une réponse IA — pour l'audit de grounding."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Claim:
    text: str
    supported: bool | None = None
    supporting_units: list[str] = field(default_factory=list)
    confidence: float | None = None


@dataclass(slots=True)
class ClaimAudit:
    claims: list[Claim] = field(default_factory=list)

    def unsupported(self) -> list[Claim]:
        return [c for c in self.claims if c.supported is not True]

    def ok(self) -> bool:
        return all(c.supported is True for c in self.claims)
