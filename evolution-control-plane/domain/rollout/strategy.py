"""Stratégie de rollout — pilotée par config/rollout-policies.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG = Path(__file__).resolve().parents[3] / "config" / "rollout-policies.yaml"

FALLBACK_PER_CLASS = {"P1": "direct", "P2": "direct", "P3": "staged", "P4": "canary",
                      "P5": "canary", "P6": "canary", "P7": "pilot", "P8": "canary",
                      "P9": "canary"}


@dataclass(frozen=True, slots=True)
class Strategy:
    name: str
    targets: list[str]
    canary_steps: list[int]
    gates: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"strategy": self.name, "targets": self.targets,
                "canary_steps": self.canary_steps, "gates": self.gates}


def strategy_for(change_class: str) -> Strategy:
    cfg: dict[str, Any] = {}
    if CONFIG.exists():
        cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    per_class = cfg.get("per_class") or FALLBACK_PER_CLASS
    name = per_class.get(change_class, "staged")
    strat = (cfg.get("strategies") or {}).get(name, {})
    slo = cfg.get("slo_gates") or {}
    gates = list(strat.get("gates", ["smoke"]))
    if slo.get("latency_p95_ms_max"):
        gates += ["metric_slo"]
    return Strategy(name=name, targets=list(strat.get("target", ["dev"])),
                    canary_steps=list(strat.get("canary_steps", [])),
                    gates=gates)
