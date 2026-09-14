"""Fixtures comportementales des règles — miroir pytest de --with-tests."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from scripts.validate_rules import TESTS_DIR, run_rule_fixtures  # noqa: E402


class TestRuleFixtures:

    def test_fixtures_presentes(self):
        files = sorted(TESTS_DIR.rglob("*.yaml"))
        families = {f.parent.name for f in files}
        assert {"safety", "malaria", "dengue", "enteric_fever", "regression"} <= families
        assert len(files) >= 7

    def test_toutes_les_fixtures_passent(self):
        passed, total, errors = run_rule_fixtures()
        assert passed == total, f"fixtures en échec : {errors}"
        assert total >= 7

    def test_format_fixture(self):
        for f in TESTS_DIR.rglob("*.yaml"):
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            assert "name" in data and "case" in data and "expect" in data, f.name
            assert "symptoms" in data["case"], f"{f.name} : cas sans symptômes"
            expect = data["expect"]
            assert any(k in expect for k in
                       ("rules_include", "urgency_at_least", "severity_at_least",
                        "isolation_required", "drugs_blocked_include")), \
                f"{f.name} : attente vide"
