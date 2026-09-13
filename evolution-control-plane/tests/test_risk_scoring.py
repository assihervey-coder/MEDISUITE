"""Verrou : scoring de risque (config risk-levels.yaml) + blast radius."""
from __future__ import annotations

from ecp.domain.assessment.blast_radius import compute_blast_radius
from ecp.domain.assessment.impact import ImpactReport
from ecp.domain.assessment.risk import compute_risk


def test_aucun_impact_ou_presque():
    rs = compute_risk({d: "NONE" for d in
                       ("patient_safety", "clinical", "data", "ai",
                        "security", "regulatory")})
    assert rs.score == 0 and rs.level == "LOW"


def test_securite_patient_high_est_critique_ou_haut():
    rs = compute_risk({"patient_safety": "HIGH", "clinical": "HIGH",
                       "data": "MEDIUM", "ai": "MEDIUM", "security": "LOW",
                       "regulatory": "LOW"})
    assert rs.score >= 40
    assert rs.level in ("HIGH", "CRITICAL")
    assert "safety_review" in rs.required_gates
    assert "clinical_review" in rs.required_gates


def test_poids_securite_patient_dominant():
    rs = compute_risk({"patient_safety": "HIGH", "clinical": "NONE",
                       "data": "NONE", "ai": "NONE", "security": "NONE",
                       "regulatory": "NONE"})
    assert rs.contributions["patient_safety"] == 35.0


def test_blast_radius_progressif():
    empty = ImpactReport()
    assert compute_blast_radius(empty, "LOW", False, False).level == "NONE"
    one = ImpactReport(services=1)
    assert compute_blast_radius(one, "LOW", False, False).level in ("LOCAL", "MODERATE")
    heavy = ImpactReport(services=3, databases=2, apis=4, clinical_rules=17)
    assert compute_blast_radius(heavy, "CRITICAL", True, True).level == "CRITICAL"


def test_breaking_change_force_blast_eleve():
    assert compute_blast_radius(ImpactReport(services=1), "LOW",
                                True, False).level in ("HIGH", "CRITICAL")


def test_to_dict_contrat_assessment():
    rs = compute_risk({"patient_safety": "LOW", "clinical": "LOW", "data": "NONE",
                       "ai": "NONE", "security": "NONE", "regulatory": "NONE"})
    payload = rs.to_dict()
    assert "risk" in payload and "score" in payload["risk"]
    assert "required_gates" in payload["risk"]
