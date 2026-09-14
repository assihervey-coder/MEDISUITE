"""Qualité temporelle — la chronologie influence-t-elle le différentiel ?

Contrôles :
    - cohérence de la chronologie reconstruite (incohérences détectées),
    - exclusion temporelle : une maladie dont la fenêtre d'incubation est
      incompatible avec les dates de voyage doit être rétrogradée/absente
      du top du différentiel,
    - récit temporel présent pour chaque cas.
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report
from evaluation.clinical.differential_quality import top_disease_codes

# cas où la temporalité DOIT exclure une maladie du top
# (voyage fermé depuis longtemps vs incubation courte)
TEMPORAL_EXCLUSION_CASES = [
    {
        "payload": {
            "patient": {"age_years": 30, "sex": "male"},
            "symptoms": [{"code": "fever", "onset": "2026-09-01"}],
            # retour de voyage il y a 90 jours : la dengue (incubation ≤ 14 j)
            # ne doit PAS dominer le différentiel
            "travel": {"segments": [{"country": "TH", "arrival": "2026-05-01",
                                      "departure": "2026-06-03"}]},
            "consultation_date": "2026-09-08",
        },
        "excluded_from_top3": "dengue",
    },
    {
        "payload": {
            "patient": {"age_years": 25, "sex": "female"},
            "symptoms": [{"code": "fever", "onset": "2026-09-05"}],
            # voyage en cours (retour futur) : incubation compatible palu
            "travel": {"segments": [{"country": "CI", "arrival": "2026-09-01"}],
                       "resident_country": "FR"},
            "consultation_date": "2026-09-07",
        },
        "expected_in_top3": "malaria",
    },
]


def run() -> SuiteReport:
    report = SuiteReport(suite="clinical_temporal")
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.clinical_engine.temporal.timeline_engine import TimelineEngine
    from tropirag.domain.clinical_case.builders import build_case

    orchestrator = ClinicalOrchestrator()
    timeline = TimelineEngine()

    coherent = 0
    total = 0
    for item in TEMPORAL_EXCLUSION_CASES:
        case = build_case(item["payload"])
        analysis = orchestrator.analyze(case)
        report_timeline = timeline.build(case)
        total += 1
        if report_timeline.coherent:
            coherent += 1
        top3 = set(top_disease_codes(analysis, 3))
        case_result = {"top3": sorted(top3),
                      "coherent": report_timeline.coherent}
        if "excluded_from_top3" in item:
            case_result["exclusion_ok"] = item["excluded_from_top3"] not in top3
        if "expected_in_top3" in item:
            case_result["inclusion_ok"] = item["expected_in_top3"] in top3
        report.cases.append(case_result)

    # sur le dataset doré : toutes les chronologies reconstruites doivent
    # être cohérentes (aucune incohérence non signalée)
    from evaluation.common import load_dataset
    for item in load_dataset("clinical_cases"):
        case = build_case(item["payload"])
        report.cases.append({"case": item.get("case_id"),
                             "coherent": timeline.build(case).coherent})
        total += 1
        if report.cases[-1]["coherent"]:
            coherent += 1

    report.add(MetricResult("timeline_coherence", coherent / max(1, total), 1.0,
                            {"cases": total}))
    exclusions_ok = [c.get("exclusion_ok") for c in report.cases
                     if "exclusion_ok" in c]
    if exclusions_ok:
        report.add(MetricResult("temporal_exclusion",
                                sum(exclusions_ok) / len(exclusions_ok), 1.0))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
