"""Objets-valeurs du domaine Proposal."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .enums import ImpactLevel

PROP_RE = re.compile(r"^PROP-\d{4}$")
CHG_RE = re.compile(r"^CHG-\d{4}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True, slots=True)
class ProposalId:
    """Identifiant immuable PROP-XXXX."""

    value: str

    def __post_init__(self) -> None:
        if not PROP_RE.match(self.value):
            raise ValueError(f"id proposition invalide : {self.value!r} (attendu PROP-XXXX)")

    def __str__(self) -> str:  # pragma: no cover — confort
        return self.value


@dataclass(frozen=True, slots=True)
class ChangeSetId:
    value: str

    def __post_init__(self) -> None:
        if not CHG_RE.match(self.value):
            raise ValueError(f"id change set invalide : {self.value!r} (attendu CHG-XXXX)")


@dataclass(frozen=True, slots=True)
class ImpactVector:
    """Vecteur d'impact déclaré par la proposition (7 dimensions)."""

    clinical: ImpactLevel = ImpactLevel.NONE
    patient_safety: ImpactLevel = ImpactLevel.NONE
    security: ImpactLevel = ImpactLevel.NONE
    data: ImpactLevel = ImpactLevel.NONE
    api: ImpactLevel = ImpactLevel.NONE
    ai: ImpactLevel = ImpactLevel.NONE
    product: ImpactLevel = ImpactLevel.NONE

    def max_level(self) -> ImpactLevel:
        order = [ImpactLevel.NONE, ImpactLevel.LOW, ImpactLevel.MEDIUM, ImpactLevel.HIGH]
        vals = {self.clinical, self.patient_safety, self.security,
                self.data, self.api, self.ai, self.product}
        return max(vals, key=order.index)


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    """Référence à un dossier de preuve EVD-*."""

    evidence_id: str
    kind: str  # impact-analysis | risk-assessment | approval | tests | ...
    created_at: str = field(default_factory=now_iso)
