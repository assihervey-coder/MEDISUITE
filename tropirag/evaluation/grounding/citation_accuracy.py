"""Exactitude des citations — marqueurs, existence, authenticité des extraits."""
from __future__ import annotations

from evaluation.common import (
    MetricResult,
    SuiteReport,
    markdown_summary,
    write_report,
)

THRESHOLD = 0.90   # 90 % des citations sans aucun problème d'intégrité


def citation_accuracy(response, pack) -> dict:
    """Vérifie l'intégrité des citations d'une réponse (0–1 + détails)."""
    from tropirag.response_engine.citation_builder import verify_citations

    r = verify_citations(response, pack)
    return {"score": 1.0 if r["passed"] else 0.0,
            "problems": r["problems"], "citations": r["citations"]}


def run(pipeline_cases: list[dict] | None = None) -> SuiteReport:
    """pipeline_cases : [{response, pack}] — si None : dataset clinique."""
    report = SuiteReport(suite="grounding_citations")
    if pipeline_cases is None:
        pipeline_cases = _collect_from_dataset()
    if not pipeline_cases:
        report.add(MetricResult("citation_accuracy", 0.0, THRESHOLD))
        write_report(report, markdown_summary(report))
        return report
    scores = [citation_accuracy(c["response"], c["pack"]) for c in pipeline_cases]
    mean = sum(s["score"] for s in scores) / len(scores)
    report.add(MetricResult("citation_accuracy", mean, THRESHOLD,
                            {"cases": len(scores)}))
    report.cases = [{"score": s["score"], "problems": s["problems"]}
                    for s in scores]
    write_report(report, markdown_summary(report))
    return report


def _collect_from_dataset() -> list[dict]:
    from evaluation.common import load_dataset
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.evidence_engine.evidence_engine import EvidenceEngine
    from tropirag.query_engine.query_planner import QueryPlanner
    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

    orchestrator = ResponseOrchestrator()
    clinical = ClinicalOrchestrator()
    engine = EvidenceEngine()
    engine.load()
    out = []
    for item in load_dataset("clinical_cases"):
        response = orchestrator.process(item["payload"])
        analysis = clinical.analyze_payload(item["payload"])
        plan = QueryPlanner().plan(analysis)
        pack = engine.retrieve_evidence(plan.retrieval_query,
                                        diseases=plan.disease_focus or None)
        out.append({"response": response, "pack": pack})
    return out


if __name__ == "__main__":
    print(markdown_summary(run()))
