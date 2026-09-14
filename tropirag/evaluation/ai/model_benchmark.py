"""Benchmark des modèles — conformité contractuelle de chaque modèle du mesh.

En mode déterministe (offline, sans GPU), ce benchmark vérifie le CONTRAT :
    - le modèle existe dans le registre,
    - ses capacités sont résolubles (registry + YAML cohérents),
    - les invariants de gouvernance sont respectés,
    - un gateway est défini pour son exécution,
    - une version est enregistrée (gouvernance des mises à jour),
    - le fallback annoncé existe bel et bien.
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report


def audit_model(m) -> dict:
    """Audit contractuel d'un modèle du registre."""
    from tropirag.ai.registry import model_metadata as meta_mod

    checks = {
        "metadata_valid": not meta_mod.validate_metadata(m),
        "gateway_declared": bool(m.provider_gateway),
        "tasks_declared": bool(m.capabilities.tasks),
        "languages_declared": bool(m.capabilities.languages),
        "no_autonomous_diagnosis": m.capabilities.autonomous_diagnosis_allowed is False,
        "vram_declared": m.vram_gb >= 0,
    }
    return checks


def run() -> SuiteReport:
    report = SuiteReport(suite="ai")
    from tropirag.ai.registry import model_versions as versions
    from tropirag.ai.registry.model_capabilities import all_invariant_violations
    from tropirag.ai.registry.model_registry import get_registry

    reg = get_registry()
    models = reg.all()
    contract_pass = 0
    for m in models:
        checks = audit_model(m)
        v = versions.latest(m.model_id)
        checks["version_registered"] = v is not None
        for fb in m.fallback_for:
            checks[f"fallback_{fb}_exists"] = reg.get(fb) is not None
        passed = all(checks.values())
        contract_pass += int(passed)
        report.cases.append({"model": m.model_id, "checks": checks,
                             "passed": passed})

    report.add(MetricResult("model_contract_rate", contract_pass / len(models), 1.0,
                            {"models": len(models)}))

    violations = all_invariant_violations()
    report.add(MetricResult("governance_invariant_rate",
                            1.0 if not violations else 0.0, 1.0,
                            {"violations": violations}))
    # couverture des tâches critiques : chaque tâche a ≥1 modèle
    from tropirag.core.enums import ClinicalTask
    uncovered = []
    for task in ClinicalTask:
        if not reg.find_by_task(task):
            uncovered.append(task.value)
    report.add(MetricResult("task_coverage",
                            1.0 if not uncovered else
                            1 - len(uncovered) / len(list(ClinicalTask)), 1.0,
                            {"uncovered": uncovered}))
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
