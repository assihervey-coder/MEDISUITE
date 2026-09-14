"""Couverture de preuve — part des unités du pack réellement citées."""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

THRESHOLD = 0.40   # part minimale du pack citée dans les synthèses


def evidence_coverage(text: str, pack) -> float:
    """Fraction des unités du pack citées dans le texte [0,1]."""
    from tropirag.ai.guards.evidence_guard import EvidenceGuard

    return EvidenceGuard().coverage(text, pack)


def response_coverage(response, pack) -> float:
    """Couverture d'une réponse RÉELLE : unités citées / unités du pack.

    Mesure sur la liste response.citations (structure de la réponse)
    + les marqueurs inline du texte complet rendu.
    """
    cited = {c.get("unit_id") for c in (response.citations or [])}
    from tropirag.ai.guards.evidence_guard import extract_citations
    inline = set(extract_citations(getattr(response, "ai_synthesis", "") or ""))
    cited |= inline
    if not pack.units:
        return 0.0
    return len(cited & {u.unit_id for u in pack.units}) / len(pack.units)


def coverage_over_cases(cases: list[dict]) -> float:
    """Couverture moyenne — cases : [{response, pack}] ou [{response_text, pack}]."""
    if not cases:
        return 0.0
    total = 0.0
    for c in cases:
        if "response" in c:
            total += response_coverage(c["response"], c["pack"])
        else:
            total += evidence_coverage(c["response_text"], c["pack"])
    return total / len(cases)


def run(pipeline_cases: list[dict] | None = None) -> SuiteReport:
    """pipeline_cases : [{response_text, pack}] — si None, exécute le pipeline
    déterministe sur le dataset clinique."""
    report = SuiteReport(suite="grounding_coverage")
    if pipeline_cases is None:
        pipeline_cases = _collect_from_dataset()
    cov = coverage_over_cases(pipeline_cases)
    report.add(MetricResult("evidence_coverage", cov, THRESHOLD,
                            {"cases": len(pipeline_cases)}))
    report.cases = [
        {"coverage": response_coverage(c["response"], c["pack"])
         if "response" in c else evidence_coverage(c["response_text"], c["pack"])}
        for c in pipeline_cases]
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
