"""Affirmations non soutenues — deux couches, deux contrats.

La réponse TropiRAG a deux origines distinctes :
    1. COUCHE DÉTERMINISTE (règles) : sa traçabilité = rule_ids + citations
       attachées — elle ne prétend JAMAIS être un texte IA,
    2. COUCHE IA (synthèse Med42/…) : chaque phrase clinique doit être
       ancrée dans le pack (garde d'hallucination, tolérance zéro).

Métriques :
    - ai_claims_grounded      : taux de textes IA sans affirmation non ancrée,
    - deterministic_traceability : taux de réponses avec citations + règles
      enregistrées (piste d'audit complète).
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

AI_GROUNDED_THRESHOLD = 1.0     # tolérance zéro sur la couche IA
TRACEABILITY_THRESHOLD = 0.90


def ai_layer_clean(response) -> bool:
    """La couche IA (si présente) passe la garde d'hallucination ?"""
    ai_text = getattr(response, "ai_synthesis", None)
    if not ai_text:
        return True  # mode déterministe : aucune affirmation IA par construction
    from tropirag.ai.guards import OutputGuard
    from tropirag.domain.evidence.entities import EvidencePack

    # pack reconstruit depuis les citations attachées (traçabilité)
    from tropirag.evidence_engine.evidence_engine import EvidenceEngine
    engine = EvidenceEngine()
    engine.load()
    by_id = {u.unit_id: u for u in engine.units}
    pack = EvidencePack(query="audit")
    for c in getattr(response, "citations", []) or []:
        u = by_id.get(c.get("unit_id"))
        if u is not None:
            pack.units.append(u)
            pack.scores[u.unit_id] = 1.0
    if pack.empty():
        return False  # texte IA sans aucune preuve → non soutenu
    return OutputGuard().check(ai_text, pack).passed


def deterministic_traceable(response, analysis=None) -> bool:
    """La couche déterministe porte sa piste d'audit complète ?"""
    has_citations = bool(getattr(response, "citations", None))
    has_rule_ids = bool(getattr(response, "audit_summary", None)) \
        or (analysis is not None and bool(analysis.matched_rule_ids))
    return has_citations and has_rule_ids


def run() -> SuiteReport:
    report = SuiteReport(suite="grounding_unsupported")
    from evaluation.common import load_dataset
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

    cases = load_dataset("clinical_cases")
    if not cases:
        report.add(MetricResult("ai_claims_grounded", 0.0, AI_GROUNDED_THRESHOLD))
        return report
    orchestrator = ResponseOrchestrator()
    clinical = ClinicalOrchestrator()

    clean = 0
    traceable = 0
    ai_texts = 0
    for item in cases:
        response = orchestrator.process(item["payload"])
        analysis = clinical.analyze_payload(item["payload"])
        ok_ai = ai_layer_clean(response)
        ok_trace = deterministic_traceable(response, analysis)
        clean += int(ok_ai)
        traceable += int(ok_trace)
        if getattr(response, "ai_synthesis", None):
            ai_texts += 1
        report.cases.append({"case": item.get("case_id"),
                             "ai_clean": ok_ai, "traceable": ok_trace})

    report.add(MetricResult("ai_claims_grounded", clean / len(cases),
                            AI_GROUNDED_THRESHOLD,
                            {"cases": len(cases), "with_ai_text": ai_texts}))
    report.add(MetricResult("deterministic_traceability", traceable / len(cases),
                            TRACEABILITY_THRESHOLD,
                            {"cases": len(cases)}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
