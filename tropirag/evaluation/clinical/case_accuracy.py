"""Exactitude des cas — les attentes du dataset doré sont-elles satisfaites ?

Métrique principale : taux de conformité globale (toutes les attentes d'un
cas doivent être satisfaites pour que le cas passe — tolérance zéro
clinique, détaillée par dimension pour le diagnostic).
"""
from __future__ import annotations

from evaluation.common import load_dataset
from evaluation.clinical.differential_quality import check_differential
from evaluation.clinical.escalation_quality import check_escalation
from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

_URGENCY_ORDER = ["routine", "priority", "emergency", "immediate"]
_SEVERITY_ORDER = ["none", "mild", "moderate", "severe", "critical"]


def check_case(analysis, expect: dict) -> dict:
    """Vérifie TOUTES les attentes d'un cas doré — verdict par dimension."""
    checks: dict[str, bool] = {}
    safety = analysis.safety

    if "urgency_at_least" in expect:
        want = expect["urgency_at_least"]
        checks["urgency"] = (_URGENCY_ORDER.index(safety.max_urgency.value)
                             >= _URGENCY_ORDER.index(want))
    if "severity_at_least" in expect:
        want = expect["severity_at_least"]
        checks["severity"] = (_SEVERITY_ORDER.index(safety.max_severity.value)
                              >= _SEVERITY_ORDER.index(want))
    if "red_flags_include" in expect:
        found = set(safety.red_flag_codes)
        checks["red_flags"] = all(rf in found for rf in expect["red_flags_include"])
    if "notifications_nonempty" in expect:
        checks["notifications"] = bool(safety.notify_public_health) \
            == bool(expect["notifications_nonempty"])
    if "ai_synthesis_allowed" in expect:
        from tropirag.ai.routing.risk_router import route_by_risk
        ai_allowed = route_by_risk(safety.max_severity,
                                  safety.max_urgency).ai_synthesis_allowed
        checks["ai_gate"] = ai_allowed == bool(expect["ai_synthesis_allowed"])

    checks.update(check_differential(analysis, expect))
    checks.update(check_escalation(analysis, expect))

    return {"passed": all(checks.values()), "checks": checks,
            "failed_dimensions": [k for k, v in checks.items() if not v]}


def run() -> SuiteReport:
    """Évalue les cas dorés (clinical_cases) + variants synthétiques."""
    report = SuiteReport(suite="clinical_accuracy")
    cases = load_dataset("clinical_cases") + load_dataset("synthetic_cases")
    if not cases:
        report.add(MetricResult("case_accuracy", 0.0, 0.95))
        return report

    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.domain.clinical_case.builders import build_case

    orchestrator = ClinicalOrchestrator()
    passed = 0
    for item in cases:
        analysis = orchestrator.analyze(build_case(item["payload"]))
        result = check_case(analysis, item.get("expect", {}))
        result["case_id"] = item.get("case_id") or item.get("id")
        report.cases.append(result)
        if result["passed"]:
            passed += 1

    accuracy = passed / len(cases)
    report.add(MetricResult("case_accuracy", accuracy, 0.95,
                            {"passed": passed, "total": len(cases)}))
    # dimensions : taux de réussite par famille de contrôle
    dims: dict[str, list[bool]] = {}
    for c in report.cases:
        for k, v in c["checks"].items():
            dims.setdefault(k, []).append(bool(v))
    for dim, values in sorted(dims.items()):
        if len(values) >= 2:  # dimension présente sur au moins 2 cas
            report.add(MetricResult(f"dim_{dim}", sum(values) / len(values), 0.95,
                                     {"n": len(values)}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
