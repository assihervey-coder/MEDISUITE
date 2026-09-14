"""Empreinte mémoire — plan de VRAM du mesh vs topologie matérielle.

Vérifie que le registre du mesh TIENT dans la topologie de déploiement
(4 nœuds × 8 GPU × 48 Go) et que chaque modèle tient sur UN GPU (sinon
TP requis → vérifier les Modelfiles).
"""
from __future__ import annotations

from evaluation.common import MetricResult, SuiteReport, markdown_summary, write_report

GPU_GB = 48.0
GPUS_PER_NODE = 8
NODES = 4
TOTAL_VRAM_GB = GPU_GB * GPUS_PER_NODE * NODES
SINGLE_GPU_MAX_GB = GPU_GB


def vram_plan() -> dict:
    """Plan d'empreinte par modèle + agrégats."""
    from tropirag.ai.registry.model_registry import get_registry

    reg = get_registry()
    plan = []
    total = 0.0
    for m in reg.all():
        needs_tp = m.vram_gb > SINGLE_GPU_MAX_GB
        plan.append({"model_id": m.model_id, "vram_gb": m.vram_gb,
                     "family": m.family, "needs_tp": needs_tp,
                     "fits_single_gpu": not needs_tp})
        total += m.vram_gb
    return {"models": plan, "total_vram_gb": total,
            "capacity_gb": TOTAL_VRAM_GB}


def run() -> SuiteReport:
    report = SuiteReport(suite="ai")
    plan = vram_plan()
    n_models = len(plan["models"])
    fits = sum(1 for m in plan["models"] if m["fits_single_gpu"])
    # les modèles > 48 Go (Med42 70B fp16) nécessitent TP=2+ — le
    # déploiement Ollama le documente ; le contrôle vérifie la cohérence
    # capacité globale vs demande
    fits_capacity = plan["total_vram_gb"] <= plan["capacity_gb"]

    report.add(MetricResult("single_gpu_fit_rate", fits / n_models, 0.70,
                            {"models": n_models,
                             "needs_tp": [m["model_id"] for m in plan["models"]
                                          if m["needs_tp"]]}))
    report.add(MetricResult("mesh_fits_cluster", 1.0 if fits_capacity else 0.0, 1.0,
                            {"total_gb": plan["total_vram_gb"],
                             "capacity_gb": plan["capacity_gb"]}))
    # marge : part de VRAM laissée libre (têtes KV, batchs, cache)
    margin = 1.0 - plan["total_vram_gb"] / plan["capacity_gb"]
    report.add(MetricResult("vram_margin", margin, 0.50,
                            {"margin_gb": round(plan["capacity_gb"] - plan["total_vram_gb"], 1)}))
    report.cases = plan["models"]
    write_report(report, markdown_summary(report))
    return report


if __name__ == "__main__":
    print(markdown_summary(run()))
