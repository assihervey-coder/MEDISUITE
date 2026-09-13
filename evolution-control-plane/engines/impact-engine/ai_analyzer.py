"""Analyseur IA — modèles/configs/lineage touchés."""
from __future__ import annotations

from pathlib import Path

CONFIGS_DIR = Path(__file__).resolve().parents[3] / "ai" / "multimodal" / "configs"


def count_model_configs() -> int:
    if not CONFIGS_DIR.exists():
        return 0
    return len(list(CONFIGS_DIR.glob("*.yaml")))


def analyze_ai(changed_paths: list[str]) -> dict:
    ai_paths = [p for p in changed_paths if p.startswith("ai/")]
    configs = [p for p in ai_paths if "/configs/" in p]
    model_cards = [p for p in changed_paths if "model-cards" in p]
    return {
        "ai_paths": ai_paths,
        "model_configs": count_model_configs(),
        "configs_touched": configs,
        "model_cards_touched": model_cards,
        "count": len(ai_paths),
    }
