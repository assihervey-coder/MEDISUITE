"""Validation clinique — gate signé (classe P7+)."""
from __future__ import annotations


class ClinicalValidation:
    def __init__(self, change_set_id: str, retrospective_cohort_done: bool,
                 reviewer: str) -> None:
        self.change_set_id = change_set_id
        self.retrospective_cohort_done = retrospective_cohort_done
        self.reviewer = reviewer

    @property
    def verdict(self) -> str:
        if not self.retrospective_cohort_done:
            return "REVIEW_REQUIRED"
        return "PASS" if self.reviewer else "REVIEW_REQUIRED"

    def to_dict(self) -> dict:
        return {"change_set_id": self.change_set_id,
                "retrospective_cohort": self.retrospective_cohort_done,
                "reviewer": self.reviewer, "verdict": self.verdict}
