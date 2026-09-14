"""Latence — mesure déterministe du pipeline (mode sans GPU).

Mesure le temps du chemin critique complet :
    build_case → analyse déterministe → retrieval → réponse.
Le mode ollama/vllm est ignoré (dépend du matériel) : ce benchmark chiffre
le PLANCHER garanti offline — ce que le terrain peut espérer au pire.

Métrique : taux de cas traités dans le budget terrain (p95 ≤ 5 s),
plus statistiques descriptives (médiane, max).
"""
from __future__ import annotations

import statistics
import time

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

# budget terrain : réponse complète en moins de 5 s sur matériel modeste
THRESHOLD_MS = 5000.0


def measure_case(payload: dict) -> float:
    """Latence ms d'un traitement complet (déterministe)."""
    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

    orchestrator = measure_case._orchestrator  # type: ignore[attr-defined]
    t0 = time.perf_counter()
    orchestrator.process(payload)
    return (time.perf_counter() - t0) * 1000.0


def run(cases: list[dict] | None = None, warmup: bool = True) -> SuiteReport:
    report = SuiteReport(suite="ai")
    if cases is None:
        from evaluation.common import load_dataset
        cases = [item["payload"] for item in load_dataset("clinical_cases")]
    if not cases:
        report.add(MetricResult("latency_budget_rate", 0.0, 1.0))
        return report

    from tropirag.response_engine.response_orchestrator import ResponseOrchestrator
    measure_case._orchestrator = ResponseOrchestrator()  # type: ignore[attr-defined]

    if warmup:  # premier passage : chargement règles + corpus + index
        measure_case(cases[0])

    latencies = []
    for payload in cases:
        ms = measure_case(payload)
        latencies.append(ms)
        report.cases.append({"latency_ms": round(ms, 2)})

    in_budget = sum(1 for ms in latencies if ms <= THRESHOLD_MS)
    lat_sorted = sorted(latencies)
    p95 = lat_sorted[max(0, int(len(lat_sorted) * 0.95) - 1)]
    report.add(MetricResult(
        "latency_budget_rate", in_budget / len(latencies), 1.0,
        {"p95_ms": round(p95, 2), "median_ms": round(statistics.median(latencies), 2),
         "max_ms": round(max(latencies), 2), "budget_ms": THRESHOLD_MS,
         "n": len(latencies)}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
