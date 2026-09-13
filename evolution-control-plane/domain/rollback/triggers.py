"""Déclencheurs de rollback — config/rollback-policies.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG = Path(__file__).resolve().parents[3] / "config" / "rollback-policies.yaml"

THRESHOLDS = {
    "error_rate": 0.01,
    "latency_p95_ms": 2000.0,
    "model_drift_psi": 0.2,
    "throughput_drop_pct": 20.0,
}


@dataclass(frozen=True, slots=True)
class Trigger:
    name: str          # error_rate|latency_p95|clinical_safety|model_drift|…|human_decision
    detail: str


def evaluate_triggers(metrics: dict[str, float], alerts: list[str],
                      human_decision: bool = False) -> list[Trigger]:
    """Retourne la liste des déclencheurs activés (vide = tout va bien)."""
    cfg: dict[str, Any] = {}
    if CONFIG.exists():
        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    triggers: list[Trigger] = []
    if metrics.get("error_rate", 0) > THRESHOLDS["error_rate"]:
        triggers.append(Trigger("error_rate", f"{metrics['error_rate']:.4f}"))
    if metrics.get("latency_p95_ms", 0) > THRESHOLDS["latency_p95_ms"]:
        triggers.append(Trigger("latency_p95", f"{metrics['latency_p95_ms']:.0f} ms"))
    if metrics.get("model_psi", 0) > THRESHOLDS["model_drift_psi"]:
        triggers.append(Trigger("model_drift", f"PSI {metrics['model_psi']:.2f}"))
    if metrics.get("throughput_drop_pct", 0) > THRESHOLDS["throughput_drop_pct"]:
        triggers.append(Trigger("performance_degradation",
                                f"-{metrics['throughput_drop_pct']:.0f} %"))
    if any(a in ("clinical_safety", "critical_alert") for a in alerts):
        immediate = [a for a in alerts if a in ("clinical_safety", "critical_alert")]
        triggers.append(Trigger(immediate[0], "alerte immédiate"))
    if human_decision:
        triggers.append(Trigger("human_decision", "décision humaine"))
    return triggers
