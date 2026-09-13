"""Cas d'usage — validation clinique (gate P7+, cohorte rétrospective)."""
from __future__ import annotations

from ...domain.validation.clinical import ClinicalValidation


def run_clinical_validation(change_set_id: str, retrospective_cohort_done: bool,
                            reviewer: str) -> dict:
    cv = ClinicalValidation(change_set_id, retrospective_cohort_done, reviewer)
    return cv.to_dict()
