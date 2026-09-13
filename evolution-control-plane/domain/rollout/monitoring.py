"""Monitoring — évaluation SLO (seuils alignés k6/EGSP : p95 ≤ 2 s)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONFIG = None  # seuils lus depuis config/rollout-policies.yaml par le moteur


@dataclass(frozen=True, slots=True)
class Metrics:
    error_rate: float = 0.0
    latency_p95_ms: float = 0.0
    clinical_alert_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"error_rate": self.error_rate,
                "latency_p95_ms": self.latency_p95_ms,
                "clinical_alert_rate": self.clinical_alert_rate}


class SloEvaluator:
    def __init__(self, error_rate_max: float = 0.01,
                 latency_p95_ms_max: float = 2000.0,
                 clinical_alert_rate_max: float = 0.001) -> None:
        self.error_rate_max = error_rate_max
        self.latency_p95_ms_max = latency_p95_ms_max
        self.clinical_alert_rate_max = clinical_alert_rate_max

    def evaluate(self, m: Metrics) -> tuple[bool, list[str]]:
        breaches: list[str] = []
        if m.error_rate > self.error_rate_max:
            breaches.append(f"error_rate {m.error_rate:.4f} > {self.error_rate_max}")
        if m.latency_p95_ms > self.latency_p95_ms_max:
            breaches.append(f"p95 {m.latency_p95_ms:.0f} ms > {self.latency_p95_ms_max:.0f} ms")
        if m.clinical_alert_rate > self.clinical_alert_rate_max:
            breaches.append(f"clinical_alert_rate {m.clinical_alert_rate:.5f} > "
                            f"{self.clinical_alert_rate_max}")
        return (not breaches), breaches
