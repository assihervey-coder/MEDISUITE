"""Cas d'usage — blast radius (amplitude d'impact)."""
from __future__ import annotations

from ...domain.assessment.blast_radius import compute_blast_radius
from ...domain.assessment.impact import ImpactReport


def calculate_blast_radius(counts: dict[str, int], risk_level: str,
                           breaking: bool, cross_domain: bool) -> dict:
    report = ImpactReport(**{k: v for k, v in counts.items()
                             if k in ImpactReport.__dataclass_fields__})
    radius = compute_blast_radius(report, risk_level, breaking, cross_domain)
    return radius.to_dict()
