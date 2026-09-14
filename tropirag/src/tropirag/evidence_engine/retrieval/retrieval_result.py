"""Résultat de retrieval — vue consolidée."""
from __future__ import annotations

from dataclasses import dataclass, field

from tropirag.evidence_engine.retrieval.hybrid_retriever import HybridResult


@dataclass(slots=True)
class RetrievalReport:
    query: str
    channel: str
    total_candidates: int = 0
    results: list[HybridResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
