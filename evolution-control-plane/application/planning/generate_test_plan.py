"""Cas d'usage — plan de tests dirigé par le test-impact-engine."""
from __future__ import annotations

from ...engines.test_impact_engine.engine import select_tests


def generate_test_plan(changed_paths: list[str], change_class: str) -> dict:
    full = int(change_class[1:]) >= 4
    return select_tests(changed_paths, full_regression=full)
