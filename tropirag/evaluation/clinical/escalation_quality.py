"""Qualité des escalades — actions, transferts, tests requis, contraintes."""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report


def _rule_entries(analysis, key: str) -> list:
    """Entrées de résultat de règles par famille (suspicions/flags/tests/…)."""
    result = analysis.rules
    return list(getattr(result, key, []) or [])


def _entry_text(entry) -> str:
    """Texte concat d'une entrée de règle (action + code + message)."""
    parts = []
    for attr in ("message", "code", "action", "test_code", "drug", "level"):
        v = getattr(entry, attr, None)
        if v is not None:
            parts.append(str(v))
    return " ".join(parts)


def check_escalation(analysis, expect: dict) -> dict:
    """Contrôles d'escalade d'un cas (booléens par dimension)."""
    checks: dict[str, bool] = {}
    if "escalation_includes" in expect:
        blob = " ".join(_entry_text(e) for e in
                        (_rule_entries(analysis, "escalations")
                         + _rule_entries(analysis, "notifications"))).lower()
        blob += " " + " ".join(analysis.escalation.messages).lower()
        for token in expect["escalation_includes"]:
            checks[f"escalation_{token}"] = token.lower().replace("_", " ") in blob \
                or token.lower() in blob
    if "suggested_tests_include" in expect:
        codes = {str(getattr(t, "test_code", ""))
                 for t in _rule_entries(analysis, "required_tests")}
        for code in expect["suggested_tests_include"]:
            checks[f"test_{code}"] = code in codes
    if "drug_constraints_include" in expect:
        drugs = {str(getattr(d, "drug", d))
                 for d in _rule_entries(analysis, "drug_constraints")}
        for drug in expect["drug_constraints_include"]:
            checks[f"drug_{drug}"] = drug in drugs
    if "expected_rule_families" in expect:
        ids = set(analysis.matched_rule_ids)
        for fam in expect["expected_rule_families"]:
            checks[f"family_{fam}"] = any(fam in rid.lower() for rid in ids)
    return checks


def run() -> SuiteReport:
    """Taux de présence des escalades attendues sur le dataset clinique."""
    report = SuiteReport(suite="clinical_escalation")
    from evaluation.common import load_dataset
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.domain.clinical_case.builders import build_case

    cases = load_dataset("clinical_cases")
    if not cases:
        report.add(MetricResult("escalation_coverage", 0.0, 0.85))
        return report
    orchestrator = ClinicalOrchestrator()
    total_checks = 0
    passed_checks = 0
    for item in cases:
        analysis = orchestrator.analyze(build_case(item["payload"]))
        checks = check_escalation(analysis, item.get("expect", {}))
        total_checks += len(checks)
        passed_checks += sum(1 for v in checks.values() if v)
        report.cases.append({"case": item.get("case_id"),
                             "checks": checks,
                             "all_passed": all(checks.values()) if checks else None})
    report.add(MetricResult("escalation_coverage",
                            passed_checks / max(1, total_checks), 0.85,
                            {"checks": total_checks}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
