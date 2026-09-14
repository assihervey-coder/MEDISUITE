"""Benchmark de routage — les décisions du routeur sont-elles sûres ?

Scénarios : matrice de risque. Le contrôle cardinal :
    un cas CRITIQUE ne doit JAMAIS recevoir de synthèse IA autonome —
    la réponse est déterministe pure (invariant G5).
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

# scénarios de routage (payload, décision attendue)
ROUTING_SCENARIOS = [
    ({"patient": {"age_years": 30}, "symptoms": [{"code": "fever"}]},
     {"ai_synthesis": "allowed_or_degraded"}),   # cas léger : IA possible
    ({"patient": {"age_years": 30}, "symptoms": [{"code": "fever", "severity": "severe"},
                                                  {"code": "coma"}]},
     {"ai_synthesis": "blocked"}),               # critique : déterministe pur
    ({"patient": {"age_years": 3}, "symptoms": [{"code": "fever"}, {"code": "petechiae"}]},
     {"ai_synthesis": "blocked"}),                # purpura enfant : critique
]


def run() -> SuiteReport:
    report = SuiteReport(suite="ai")
    from tropirag.ai.routing.risk_router import route_by_risk
    from tropirag.clinical_engine.orchestrator import ClinicalOrchestrator
    from tropirag.core.enums import Severity, Urgency
    from tropirag.domain.clinical_case.builders import build_case

    orchestrator = ClinicalOrchestrator()
    correct = 0
    for payload, expect in ROUTING_SCENARIOS:
        analysis = orchestrator.analyze(build_case(payload))
        risk = route_by_risk(analysis.safety.max_severity,
                             analysis.safety.max_urgency)
        ai_allowed = risk.ai_synthesis_allowed
        want = expect["ai_synthesis"]
        if want == "blocked":
            ok = not ai_allowed
            detail = "critique → synthèse IA suspendue (" + risk.reason[:60] + "…)"
        else:
            # cas non critique : le blocage n'est pas exigé, mais jamais
            # un diagnostic autonome — le pipeline reste garde
            ok = True
            detail = "cas léger — routage déterministe + garde"
        correct += int(ok)
        report.cases.append({"ai_allowed": ai_allowed, "expected": want,
                             "ok": ok, "detail": detail})

    report.add(MetricResult("routing_safety", correct / len(ROUTING_SCENARIOS), 1.0,
                            {"scenarios": len(ROUTING_SCENARIOS)}))

    # invariant cardinal renforcé : TOUT couple (sévère/critique, urgence
    # haute) doit suspendre la synthèse — matrice exhaustive
    blocked_ok = 0
    blocked_total = 0
    for sev in (Severity.SEVERE, Severity.CRITICAL):
        for urg in (Urgency.PRIORITY, Urgency.EMERGENCY, Urgency.IMMEDIATE):
            blocked_total += 1
            if not route_by_risk(sev, urg).ai_synthesis_allowed:
                blocked_ok += 1
            else:
                report.cases.append({"matrix_hole": f"{sev.value}+{urg.value}"})
    report.add(MetricResult("critical_matrix_blocks_ai",
                            blocked_ok / max(1, blocked_total), 1.0,
                            {"cells": blocked_total}))

    # routage par capacité : pour chaque tâche, le routeur propose un modèle
    from tropirag.ai.registry.model_registry import get_registry
    from tropirag.core.enums import ClinicalTask
    reg = get_registry()
    routed = 0
    total = 0
    for task in ClinicalTask:
        total += 1
        candidates = reg.find_by_task(task)
        if candidates:
            routed += 1
        else:
            report.cases.append({"task_unroutable": task.value})
    report.add(MetricResult("task_routability", routed / max(1, total), 0.80,
                            {"tasks": total}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
