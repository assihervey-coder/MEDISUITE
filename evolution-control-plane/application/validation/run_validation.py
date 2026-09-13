"""Cas d'usage — validation consolidée d'un change set."""
from __future__ import annotations

from typing import Any

from ...engines.compatibility_engine.engine import check as compat_check


def run_validation(change_set: dict, test_plan: dict,
                   facts: dict[str, Any] | None = None) -> dict[str, Any]:
    compatibility = compat_check(change_set["id"], facts or {})
    technical = "PASS" if test_plan.get("suites") else "NOT_RUN"
    clinical = "REVIEW_REQUIRED" if facts and facts.get("clinical_touched") \
        else "NOT_APPLICABLE"
    safety = "REVIEW_REQUIRED" if facts and facts.get("safety_touched") \
        else "NOT_APPLICABLE"
    return {
        "change_set": change_set["id"],
        "plan": {"selected_tests": test_plan.get("affected_tests", {}),
                 "full_regression": test_plan.get("mandatory_full_regression", False),
                 "suites": test_plan.get("suites", [])},
        "results": {"technical": technical,
                    "compatibility": compatibility["overall"],
                    "clinical": clinical, "safety": safety},
        "compatibility_detail": compatibility,
    }
