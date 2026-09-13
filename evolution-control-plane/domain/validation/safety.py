"""Validation sûreté — gate ISO 14971 (classes P7+)."""
from __future__ import annotations


class SafetyValidation:
    def __init__(self, change_set_id: str, fmea_updated: bool,
                 new_hazards_assessed: bool, safety_officer: str) -> None:
        self.change_set_id = change_set_id
        self.fmea_updated = fmea_updated
        self.new_hazards_assessed = new_hazards_assessed
        self.safety_officer = safety_officer

    @property
    def verdict(self) -> str:
        ok = self.fmea_updated and self.new_hazards_assessed and self.safety_officer
        return "PASS" if ok else "REVIEW_REQUIRED"

    def to_dict(self) -> dict:
        return {"change_set_id": self.change_set_id, "fmea_updated": self.fmea_updated,
                "new_hazards_assessed": self.new_hazards_assessed,
                "safety_officer": self.safety_officer, "verdict": self.verdict}
