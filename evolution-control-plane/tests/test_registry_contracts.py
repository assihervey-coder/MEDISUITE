"""Verrou : cohérence registre, configs, contrats JSON Schema, baseline, CI."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ECP = ROOT / "evolution-control-plane"


def _yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_registre_propositions_parse_et_seede():
    data = _yaml(ROOT / "governance" / "proposals" / "registry" / "proposals.yaml")
    ids = [p["id"] for p in data["proposals"]]
    assert len(ids) >= 10
    assert "PROP-0027" in ids  # Patient Digital Twin (exemple du cadrage)
    for p in data["proposals"]:
        assert p["status"] in {"DRAFT", "SUBMITTED", "VALIDATED", "CLASSIFIED",
                               "IMPACT_ANALYSIS", "RISK_ASSESSMENT",
                               "DECISION_PENDING", "APPROVED", "REJECTED",
                               "DEFERRED", "ACCEPTED"}
        for impact in ("clinical_impact", "patient_safety_impact", "security_impact",
                       "data_impact", "api_impact", "ai_impact"):
            assert p[impact] in {"NONE", "LOW", "MEDIUM", "HIGH"}, p["id"]


def test_sept_configs_machine_presentes_et_valides():
    for name in ("evolution", "risk-levels", "change-types", "approval-matrix",
                 "rollout-policies", "rollback-policies", "compatibility-policies"):
        assert _yaml(ECP / "config" / f"{name}.yaml") is not None


def test_sept_schemas_json_evolution_valides():
    for name in ("proposal", "assessment", "decision", "change", "validation",
                 "rollout", "rollback"):
        schema = json.loads((ROOT / "contracts" / "evolution" /
                             f"{name}.schema.json").read_text(encoding="utf-8"))
        assert schema["$schema"].startswith("http")
        assert schema["type"] == "object"
        assert schema.get("required")


def test_proposition_exemple_valide_le_schema():
    schema = json.loads((ROOT / "contracts" / "evolution" /
                         "proposal.schema.json").read_text(encoding="utf-8"))
    registry = _yaml(ROOT / "governance" / "proposals" / "registry" / "proposals.yaml")
    twin = next(p for p in registry["proposals"] if p["id"] == "PROP-0027")
    # champs requis présents et types corrects (vérification manuelle draft-07)
    for field in schema["required"]:
        assert field in twin, f"champ requis absent : {field}"
    assert twin["version"] >= 1 and isinstance(twin["title"], str)


def test_baseline_architecture_reflete_le_repo():
    services = _yaml(ROOT / "architecture" / "baseline" / "SERVICES.yaml")
    names = [s["name"] for s in services["services"]]
    for svc in ("api-gateway", "auth-service", "patient-service", "imaging-service",
                "laboratory-service", "ecrf-service", "dicom-gateway", "hl7-gateway"):
        assert svc in names
    modules = _yaml(ROOT / "architecture" / "baseline" / "CLINICAL_MODULES.yaml")
    assert modules["clinical_modules"]["count"] == 26


def test_workflows_declaratifs_presents():
    for name in ("proposal-lifecycle", "impact-analysis", "approval",
                 "implementation", "validation", "rollout", "rollback"):
        data = _yaml(ECP / "workflows" / f"{name}.yaml")
        assert data["steps"]


def test_ci_inclut_le_control_plane():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "evolution-control-plane/tests/" in ci, \
        "le job packages-integration doit exécuter les tests du control plane"


def test_gouvernance_complette():
    gov = ROOT / "governance" / "evolution"
    attendus = {"EVOLUTION_GOVERNANCE.md", "EVOLUTION_LIFECYCLE.md",
                "EVOLUTION_POLICY.md", "CHANGE_CLASSIFICATION.md",
                "APPROVAL_POLICY.md", "ROLLBACK_POLICY.md",
                "COMPATIBILITY_POLICY.md", "CLINICAL_CHANGE_POLICY.md",
                "AI_CHANGE_POLICY.md", "DATA_CHANGE_POLICY.md",
                "SECURITY_CHANGE_POLICY.md", "REGULATORY_CHANGE_POLICY.md"}
    for name in attendus:
        assert (gov / name).exists(), f"politique manquante : {name}"
    assert (ROOT / "governance" / "adr" / "accepted" /
            "ADR-0001-evolution-control-plane.md").exists()


def test_sept_templates_de_propositions():
    templates = (ROOT / "governance" / "proposals" / "templates").glob("*_PROPOSAL.yaml")
    assert len(list(templates)) == 7
