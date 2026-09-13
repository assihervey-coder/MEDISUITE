"""Blast radius — amplitude de l'explosion d'impact."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .impact import ImpactReport

LEVELS = ["NONE", "LOCAL", "MODERATE", "HIGH", "CRITICAL"]


@dataclass(frozen=True, slots=True)
class BlastRadius:
    level: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"blast_radius": {"level": self.level, "reason": self.reason}}


def compute_blast_radius(report: ImpactReport, risk_level: str,
                         breaking: bool, cross_domain: bool) -> BlastRadius:
    """Règle simple et auditable : surfaces touchées + risque + breaking."""
    index = 0
    reasons: list[str] = []
    if report.services >= 1:
        index += 1
        reasons.append(f"{report.services} service(s)")
    if report.databases >= 1 or report.apis >= 2:
        index += 1
        reasons.append("DB/API multiples")
    if report.ai_models >= 1 or report.clinical_rules >= 1:
        index += 1
        reasons.append("IA/règles cliniques")
    if breaking:
        index = max(index, 3)
        reasons.append("breaking change")
    if cross_domain:
        index += 1
        reasons.append("multi-domaines")
    if risk_level in ("HIGH", "CRITICAL"):
        index = max(index, 3)
        reasons.append(f"risque {risk_level}")
    level = LEVELS[min(index, 4)]
    return BlastRadius(level=level, reason=", ".join(reasons) or "aucune surface touchée")
