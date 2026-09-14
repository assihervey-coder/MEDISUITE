"""Alias résultats reranking."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RerankResult:
    method: str = "deterministic_lexical"
    scores: list[tuple[str, float]] = field(default_factory=list)
    model_id: str | None = None
