"""Latency Router — budgets par étape clinique."""
from __future__ import annotations

LATENCY_BUDGETS_MS: dict[str, float] = {
    "dictation": 3000,
    "conversation": 5000,
    "embed": 200,
    "rerank": 800,
    "image_triage": 5000,
    "image_analysis": 15000,
    "logical_audit": 30000,
    "clinical_synthesis": 60000,
    "biomedical_synthesis": 90000,
    "segmentation": 20000,
}


def budget_for(step: str) -> float:
    return LATENCY_BUDGETS_MS.get(step, 30000.0)
