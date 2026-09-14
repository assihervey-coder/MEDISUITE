"""Adapter Qwen Reranker."""
from __future__ import annotations

from typing import Any


def parse_rerank(structured: Any) -> list[float]:
    if isinstance(structured, dict) and "scores" in structured:
        return [float(s) for s in structured["scores"]]
    return []
