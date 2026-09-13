"""Plan de validation — consolidation des étapes techniques/cliniques/sûreté."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationPlan:
    change_set_id: str
    full_regression: bool
    selected_tests: dict[str, int]          # {suite: nombre de tests}
    compatibility_required: bool = True
    clinical_review_required: bool = False
    safety_review_required: bool = False
    regulatory_review_required: bool = False
    notes: list[str] = field(default_factory=list)

    def total_selected(self) -> int:
        return sum(self.selected_tests.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_set_id": self.change_set_id,
            "plan": {
                "selected_tests": self.selected_tests,
                "total": self.total_selected(),
                "full_regression": self.full_regression,
                "compatibility_required": self.compatibility_required,
                "clinical_review_required": self.clinical_review_required,
                "safety_review_required": self.safety_review_required,
                "regulatory_review_required": self.regulatory_review_required,
                "notes": self.notes,
            },
        }
