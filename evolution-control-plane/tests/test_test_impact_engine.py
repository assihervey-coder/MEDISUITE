"""Verrou : test-impact engine (sélection réelle sur les suites du repo)."""
from __future__ import annotations

from ecp.engines.test_impact_engine.engine import (dependency_mapper,
                                                   needs_full_regression,
                                                   select_tests)


def test_selection_ciblee_service():
    plan = select_tests(["services/patient-service/tests/test_patient.py"],
                        full_regression=False)
    assert "services/patient-service/tests/" in plan["suites"]
    assert plan["mandatory_full_regression"] is False


def test_selection_core_et_regles():
    plan = select_tests(["packages/medisuite-core/medisuite_core/ecrf.py",
                         "packages/clinical-rules/medisuite_rules/cardiology.py"],
                        full_regression=False)
    assert "packages/medisuite-core/tests/" in plan["suites"]
    assert "packages/clinical-rules/tests/" in plan["suites"]


def test_regression_complete_p4_et_plus():
    assert needs_full_regression("P4") is True
    assert needs_full_regression("P9") is True
    assert needs_full_regression("P3") is False
    plan = select_tests(["services/api-gateway/src/main.py"], full_regression=True)
    for suite in ("packages/medisuite-core/tests/", "packages/clinical-rules/tests/",
                  "datasets/tests/", "tools/tests/"):
        assert suite in plan["suites"]


def test_comptage_tests_reel_non_nul():
    plan = select_tests(["packages/medisuite-core/medisuite_core/fhir.py"],
                        full_regression=False)
    assert plan["affected_tests"].get("medisuite-core", 0) > 0


def test_mapper_composants_connus():
    mapping = dependency_mapper(["ai/multimodal/core/torch_fusion.py",
                                 "datasets/manifest.json"])
    assert "ai-multimodal" in mapping
    assert "datasets" in mapping
