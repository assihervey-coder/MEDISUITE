"""Risque — scoring pondéré piloté par config/risk-levels.yaml (ISO 14971)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG = Path(__file__).resolve().parents[3] / "config" / "risk-levels.yaml"

DEFAULT_WEIGHTS = {"patient_safety": 35, "clinical": 20, "data": 15,
                   "ai": 10, "security": 10, "regulatory": 10}
DEFAULT_VALUES = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
DEFAULT_BANDS = {"LOW": (0, 15), "MEDIUM": (16, 39), "HIGH": (40, 69),
                 "CRITICAL": (70, 100)}


def _load() -> dict[str, Any]:
    if CONFIG.exists():
        return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    return {}


@dataclass(frozen=True, slots=True)
class RiskScore:
    score: int
    level: str            # LOW | MEDIUM | HIGH | CRITICAL
    weights: dict[str, int]
    contributions: dict[str, int]
    required_gates: list[str]
    max_change_class: str

    def to_dict(self) -> dict[str, Any]:
        return {"risk": {"score": self.score, "level": self.level,
                         "contributions": self.contributions,
                         "required_gates": self.required_gates,
                         "max_change_class": self.max_change_class}}


def compute_risk(impacts: dict[str, str]) -> RiskScore:
    """impacts : {dimension: NONE|LOW|MEDIUM|HIGH} → score pondéré 0..100."""
    cfg = _load()
    scoring = cfg.get("scoring", {})
    weights = scoring.get("weights", DEFAULT_WEIGHTS)
    values = scoring.get("impact_values", DEFAULT_VALUES)
    contributions: dict[str, int] = {}
    total = 0
    for dim, weight in weights.items():
        c = weight * values.get((impacts.get(dim) or "NONE").upper(), 0) / 3
        contributions[dim] = round(c, 1)
        total += c
    score = round(min(total, 100))
    levels = cfg.get("levels", {})
    level = "CRITICAL"
    for name, band in (levels or DEFAULT_BANDS).items():
        lo, hi = band["score"] if isinstance(band, dict) and "score" in band else DEFAULT_BANDS[name]
        if lo <= score <= hi:
            level = name
            break
    else:  # bande manquante → règle de bandes par défaut
        for name, (lo, hi) in DEFAULT_BANDS.items():
            if lo <= score <= hi:
                level = name
                break
    lvl_cfg = (levels or {}).get(level, {})
    gates = lvl_cfg.get("required_gates", DEFAULT_GATES[level]) if lvl_cfg else DEFAULT_GATES[level]
    max_class = lvl_cfg.get("max_change_class", "P3") if lvl_cfg else "P3"
    return RiskScore(score=score, level=level, weights=dict(weights),
                     contributions=contributions, required_gates=list(gates),
                     max_change_class=max_class)


DEFAULT_GATES = {
    "LOW": ["technical_validation"],
    "MEDIUM": ["technical_validation", "compatibility_review"],
    "HIGH": ["technical_validation", "compatibility_review", "safety_review"],
    "CRITICAL": ["technical_validation", "compatibility_review", "safety_review",
                 "clinical_review", "regulatory_review"],
}
