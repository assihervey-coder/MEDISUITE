"""Qualité du différentiel — rang de la maladie attendue, calibration."""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report


def top_disease_codes(analysis, n: int | None = None) -> list[str]:
    """Codes de maladie du différentiel, dans l'ordre (exclusions incluses)."""
    return [str(d.disease) for d in analysis.differentials[: n]]


def check_differential(analysis, expect: dict) -> dict:
    """Contrôles différentiels d'un cas (booléens par dimension)."""
    checks: dict[str, bool] = {}
    if "top_differential" in expect:
        top = top_disease_codes(analysis, 1)
        checks["top_differential"] = bool(top) and top[0] == expect["top_differential"]
    if "differential_in_top3" in expect:
        top3 = set(top_disease_codes(analysis, 3))
        expected_set = set(expect["differential_in_top3"])
        checks["differential_top3"] = bool(top3 & expected_set)
    return checks


def hit_rate(analyses: list, expectations: list[dict], top_n: int = 3) -> float:
    """Taux de présence de la maladie attendue dans le top-N."""
    if not analyses:
        return 0.0
    hits = 0
    for analysis, expect in zip(analyses, expectations):
        top = set(top_disease_codes(analysis, top_n))
        if top & set(expect.get("differential_in_top3", [])):
            hits += 1
    return hits / len(analyses)


def calibration_error(analysis, expected_prob: float, disease: str) -> float:
    """Erreur absolue entre score prédit et attendu (calibration)."""
    for d in analysis.differentials:
        if str(d.disease) == disease:
            return abs(d.score - expected_prob)
    return 1.0


def run() -> SuiteReport:
    """Rang de la maladie attendue dans le différentiel (dataset clinique)."""
    report = SuiteReport(suite="clinical_differential")
    from evaluation.common import load_dataset
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.domain.clinical_case.builders import build_case

    cases = load_dataset("clinical_cases")
    if not cases:
        report.add(MetricResult("differential_hit_rate_top3", 0.0, 0.90))
        return report
    orchestrator = ClinicalOrchestrator()
    analyses = [orchestrator.analyze(build_case(c["payload"])) for c in cases]
    expectations = [c.get("expect", {}) for c in cases]

    top1 = 0
    top1_expected = 0
    top3 = 0
    for analysis, expect in zip(analyses, expectations):
        top = top_disease_codes(analysis, 3)
        if "top_differential" in expect:
            top1_expected += 1
            if top and top[0] == expect["top_differential"]:
                top1 += 1
        if set(top) & set(expect.get("differential_in_top3", [])):
            top3 += 1

    report.add(MetricResult("differential_top1_rate",
                            top1 / max(1, top1_expected), 0.50,
                            {"n_with_expectation": top1_expected,
                             "total_cases": len(cases)}))
    report.add(MetricResult("differential_hit_rate_top3", top3 / len(cases), 0.90,
                            {"n": len(cases)}))
    report.cases = [{"case": c.get("case_id"),
                     "top3": top_disease_codes(a, 3)}
                    for c, a in zip(cases, analyses)]
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
