"""Métriques de retrieval."""
from __future__ import annotations

from tropirag.observability.metrics import Metrics


def track_retrieval(query_id: str, candidates: int, kept: int, duration_ms: float) -> None:
    m = Metrics.instance()
    m.inc("tropirag_retrieval_total")
    m.observe("tropirag_retrieval_ms", duration_ms, query_id=query_id[:20])
    m.inc("tropirag_retrieval_candidates", candidates)
    m.inc("tropirag_retrieval_kept", kept)
