"""Régression — verdict de suite complète (obligatoire P4+)."""
from __future__ import annotations


def regression_required(change_class: str) -> bool:
    return int(change_class[1:]) >= 4


class RegressionResult:
    def __init__(self, passed: int, failed: int, suites: list[str]) -> None:
        self.passed = passed
        self.failed = failed
        self.suites = suites

    @property
    def verdict(self) -> str:
        return "PASS" if self.failed == 0 else "FAIL"

    def to_dict(self) -> dict:
        return {"passed": self.passed, "failed": self.failed,
                "suites": self.suites, "verdict": self.verdict}
