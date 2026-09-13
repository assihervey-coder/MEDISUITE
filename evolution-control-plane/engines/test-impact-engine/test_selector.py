"""Sélecteur de tests — affected_tests par catégorie + suites réelles."""
from __future__ import annotations

from pathlib import Path

from .dependency_mapper import dependency_mapper

ROOT = Path(__file__).resolve().parents[3]


def count_tests_in_suite(suite: str) -> int:
    """Compte les fonctions de test dans une suite pytest réelle."""
    base = ROOT / suite
    if not base.exists():
        return 0
    total = 0
    files = list(base.rglob("test_*.py")) if base.is_dir() else []
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("def test_") or s.startswith("async def test_"):
                total += 1
    return total


def select_tests(changed_paths: list[str], full_regression: bool) -> dict:
    mapping = dependency_mapper(changed_paths)
    suites: list[str] = []
    affected: dict[str, int] = {}
    for comp, comp_suites in sorted(mapping.items()):
        for suite in comp_suites:
            if suite not in suites:
                suites.append(suite)
            n = count_tests_in_suite(suite)
            affected[comp] = affected.get(comp, 0) + n
    if full_regression:
        # régression complète : toutes les suites pytest connues du repo
        full = ["packages/medisuite-core/tests/", "packages/clinical-rules/tests/",
                "datasets/tests/", "tools/tests/",
                "services/integration-service/tests/",
                "evolution-control-plane/tests/"]
        for s in full:
            if s not in suites:
                suites.append(s)
    return {
        "affected_tests": affected,
        "suites": suites,
        "mandatory_full_regression": full_regression,
    }
