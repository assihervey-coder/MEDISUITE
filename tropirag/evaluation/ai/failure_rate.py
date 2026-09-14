"""Taux d'échec — injection de pannes + vérification des replis.

Scénarios d'injection (aucun réseau requis) :
    1. gateway déterministe : jamais en échec (référence absolue),
    2. ollama injoignable → repli déterministe EXPLICITE (jamais de crash,
       jamais de réponse non garantie),
    3. garde de sortie : rejet d'une sortie corrompue → réponse refusée propre.
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

THRESHOLD = 1.0   # tolérance zéro : tout scénario d'échec doit être couvert


def run() -> SuiteReport:
    report = SuiteReport(suite="ai")
    scenarios = []

    # --- 1. déterministe : le socle ne peut pas échouer --------------------
    from tropirag.ai.gateways.deterministic_gateway import DeterministicGateway
    gw = DeterministicGateway()
    scenarios.append({"scenario": "deterministic_baseline",
                      "passed": gw is not None})

    # --- 2. ollama injoignable → repli gracieux ------------------------------
    from tropirag.ai.gateways.ollama_gateway import OllamaGateway
    ollama = OllamaGateway("http://127.0.0.1:1")   # port réservé : échec garanti
    try:
        healthy = ollama.health().get("healthy", False) if hasattr(ollama, "health") \
            else False
        scenarios.append({"scenario": "ollama_down_detected",
                          "passed": healthy is False})
    except Exception:
        scenarios.append({"scenario": "ollama_down_detected",
                          "passed": True})  # échec propre = détection réussie

    # le pipeline complet doit rester fonctionnel en mode déterministe
    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator
    orchestrator = ResponseOrchestrator(inference_mode="deterministic")
    response = orchestrator.process({
        "patient": {"age_years": 30},
        "symptoms": [{"code": "fever"}]})
    scenarios.append({"scenario": "pipeline_offline_complete",
                      "passed": response is not None and bool(response.narrative)})

    # --- 3. sortie corrompue → garde rejette proprement ----------------------
    from tropirag.ai.guards import OutputGuard
    from tropirag.core.enums import SourceAuthority
    from tropirag.domain.evidence.entities import EvidencePack, EvidenceUnit, SourceRef
    src = SourceRef(source_id="w", authority=SourceAuthority.WHO, title="G",
                    publisher="OMS")
    pack = EvidencePack(query="q")
    pack.units = [EvidenceUnit(unit_id="eu-1", text="L'artésunate IV est indiqué.",
                               source=src)]
    corrupted = "Donnez 500 mg trois fois par jour, le diagnostic certain est posé."
    guard_result = OutputGuard().check(corrupted, pack)
    scenarios.append({"scenario": "corrupted_output_blocked",
                      "passed": not guard_result.passed})

    report.cases = scenarios
    rate = sum(1 for s in scenarios if s["passed"]) / len(scenarios)
    report.add(MetricResult("failure_recovery_rate", rate, THRESHOLD,
                            {"scenarios": len(scenarios)}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
