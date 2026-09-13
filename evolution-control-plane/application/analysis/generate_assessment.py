"""Cas d'usage — dossier d'assessment consolidé (impact + risque + blast)."""
from __future__ import annotations

from typing import Any

from ...domain.assessment.blast_radius import compute_blast_radius
from ...domain.assessment.complexity import compute_complexity
from ...domain.assessment.entities import Assessment, AssessmentRepository
from ...domain.assessment.impact import ImpactReport
from ...domain.assessment.risk import compute_risk
from ...engines.impact_engine.engine import analyze


def generate_assessment(proposal_id: str, changed_paths: list[str],
                        impacts: dict[str, str], breaking: bool,
                        cross_domain: bool, complexity_flags: dict[str, bool] | None = None,
                        store: AssessmentRepository | None = None) -> dict[str, Any]:
    result = analyze(changed_paths)
    impact = ImpactReport(
        files=result.files, services=result.services, databases=result.databases,
        apis=result.apis, events=result.events, ai_models=result.ai_models,
        clinical_rules=result.clinical_rules)
    risk = compute_risk(impacts)
    radius = compute_blast_radius(impact, risk.level, breaking, cross_domain)
    complexity = compute_complexity(complexity_flags or {})
    assessment = Assessment(
        proposal_id=proposal_id, impact=impact, risk=risk, blast_radius=radius,
        breaking_changes_detected=breaking,
        migration_required=result.databases > 0 or bool(complexity_flags and complexity_flags.get("migration")),
        complexity=complexity.to_dict())
    payload = assessment.to_dict()
    if store is not None:
        store.save(assessment)
    return payload
