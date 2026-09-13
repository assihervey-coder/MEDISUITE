"""Acceptation finale — verrou de la nouvelle baseline (MONITORED → ACCEPTED)."""
from __future__ import annotations


class AcceptanceCriteria:
    def __init__(self, release_id: str, soak_days: int, slo_respected: bool,
                 no_open_safety_issue: bool, evidence_complete: bool) -> None:
        self.release_id = release_id
        self.soak_days = soak_days
        self.slo_respected = slo_respected
        self.no_open_safety_issue = no_open_safety_issue
        self.evidence_complete = evidence_complete

    @property
    def accepted(self) -> bool:
        return (self.soak_days >= 14 and self.slo_respected
                and self.no_open_safety_issue and self.evidence_complete)

    def to_dict(self) -> dict:
        return {"release_id": self.release_id, "soak_days": self.soak_days,
                "slo_respected": self.slo_respected,
                "no_open_safety_issue": self.no_open_safety_issue,
                "evidence_complete": self.evidence_complete,
                "accepted": self.accepted}
