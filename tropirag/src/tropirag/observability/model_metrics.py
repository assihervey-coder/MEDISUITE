"""Métriques par modèle du mesh."""
from __future__ import annotations

from tropirag.observability.metrics import Metrics


def track_inference(model_id: str, gateway: str, ok: bool, latency_ms: float) -> None:
    m = Metrics.instance()
    m.inc("tropirag_inference_total", 1.0, model=model_id, status="ok" if ok else "fail")
    if ok:
        m.observe("tropirag_inference_ms", latency_ms, model=model_id, gateway=gateway)
