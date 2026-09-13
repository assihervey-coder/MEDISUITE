"""Verrou : compatibility engine (9 dimensions, verdict global agrégé)."""
from __future__ import annotations

from ecp.engines.compatibility_engine.engine import check


def test_rien_ne_change_not_applicable():
    report = check("CHG-0001", {})
    assert report["overall"] == "PASS"  # config PASS par défaut, autres N/A
    assert report["compatibility"]["dicom"] == "NOT_APPLICABLE"


def test_drop_column_est_un_echec_dur():
    report = check("CHG-0002", {"drop_columns": ["patients.ssn"],
                                "expand_only": False})
    assert report["compatibility"]["database"] == "FAIL"
    assert report["overall"] == "FAIL"


def test_expand_only_passe():
    report = check("CHG-0003", {"expand_only": True})
    assert report["compatibility"]["database"] == "PASS"


def test_breaking_api_exige_revue():
    report = check("CHG-0004", {
        "endpoints_before": {"/patients": "GET,v1"},
        "endpoints_after": {"/patients": "GET,v2"},
    })
    assert report["compatibility"]["api"] == "REVIEW_REQUIRED"
    assert report["overall"] == "REVIEW_REQUIRED"


def test_dicom_sop_class_est_bloquant():
    report = check("CHG-0005", {"dicom_sop_changed": True})
    assert report["compatibility"]["dicom"] == "FAIL"


def test_ia_lineage_incomplet_warning_seuil_exige_revue():
    warn = check("CHG-0006", {"model_changed": True, "lineage_complete": False})
    assert warn["compatibility"]["ai"] == "WARNING"
    seuil = check("CHG-0007", {"model_changed": True, "lineage_complete": True,
                               "threshold_changed": True})
    assert seuil["compatibility"]["ai"] == "REVIEW_REQUIRED"


def test_clinique_touchee_exige_toujours_revue():
    report = check("CHG-0008", {"clinical_touched": True})
    assert report["compatibility"]["clinical"] == "REVIEW_REQUIRED"


def test_fhir_profil_r6_isole():
    report = check("CHG-0009", {"fhir_profiles": ["StructureDefinition-Patient-CI-IOP.json"]})
    assert report["compatibility"]["fhir"] == "REVIEW_REQUIRED"
    assert "ADR-0024" in report["details"]["fhir"]
