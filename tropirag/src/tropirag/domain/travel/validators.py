"""Validation de cohérence du voyage."""
from __future__ import annotations

from tropirag.domain.travel.entities import TravelSegment


def validate_segment(seg: TravelSegment) -> list[str]:
    issues: list[str] = []
    if seg.arrival and seg.departure and seg.departure < seg.arrival:
        issues.append(f"Segment {seg.country}: départ avant arrivée")
    if not seg.country or len(seg.country) != 2:
        issues.append("Code pays invalide (ISO-2 attendu)")
    return issues
