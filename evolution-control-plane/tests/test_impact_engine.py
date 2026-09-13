"""Verrou : impact engine sur le VRAI repo (baseline dérivée des sources)."""
from __future__ import annotations

from ecp.engines.impact_engine.engine import analyze
from ecp.engines.impact_engine.clinical_analyzer import count_clinical_rules
from ecp.engines.impact_engine.ai_analyzer import count_model_configs


def test_service_unique_detecte():
    r = analyze(["services/patient-service/src/main.py",
                 "services/patient-service/tests/test_patient.py"])
    assert r.services == 1
    assert r.files == 2
    assert r.components.get("patient-service") == 2


def test_regles_cliniques_comptees():
    r = analyze(["packages/clinical-rules/medisuite_rules/scores.py"])
    assert r.clinical_rules >= 1
    assert count_clinical_rules() >= 12  # modules de règles réels


def test_ia_detectee_avec_26_configs():
    r = analyze(["ai/multimodal/core/gated_fusion.py"])
    assert r.ai_models == 1
    assert count_model_configs() == 26  # 26 spécialités


def test_migration_db_detectee():
    r = analyze(["migrations/database/expand/001_add_column.sql"])
    assert r.databases == 1


def test_fichiers_inexistants_signales():
    r = analyze(["services/ghost-service/src/main.py"])
    assert r.details["code"]["files_existing"] == 0
    assert r.files == 1  # compté quand même, mais reality-check fourni


def test_securite_et_conformite():
    r = analyze(["security/hardening/vault/init_secrets.sh",
                 "compliance/mdr/technical-documentation/03-analyse-risques.md"])
    assert r.details["security"]["count"] >= 1
    assert r.details["compliance"]["count"] >= 1
