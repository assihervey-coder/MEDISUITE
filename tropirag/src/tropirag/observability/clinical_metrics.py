"""Métriques cliniques — gravité, urgence, refus."""
from __future__ import annotations

from tropirag.observability.metrics import Metrics


def track_clinical(urgency: str, severity: str, ai_layer: str, refused: bool) -> None:
    m = Metrics.instance()
    m.inc("tropirag_cases_total")
    m.inc("tropirag_urgency_total", 1.0, urgency=urgency)
    m.inc("tropirag_severity_total", 1.0, severity=severity)
    m.inc("tropirag_ai_layer_total", 1.0, layer=ai_layer)
    if refused:
        m.inc("tropirag_refusals_total")
