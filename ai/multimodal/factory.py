"""Factory : construit un FusionEngine depuis une config YAML (configs/*.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml

from .core.fusion_engine import FusionEngine

CONFIG_DIR = Path(__file__).resolve().parent / "configs"


def engine_from_config(config_path: str | Path) -> FusionEngine:
    """Construit un moteur depuis un YAML de module (01_imaging.yaml … 26_emergency)."""
    with open(config_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return FusionEngine(
        d_model=int(cfg.get("d_model", 32)),
        task=cfg.get("task", "classification"),
        seed=int(cfg.get("seed", 42)),
    )


def engine_for_module(module_no: int) -> FusionEngine:
    """Raccourci : module 8 → configs/08_cardiology.yaml."""
    files = sorted(CONFIG_DIR.glob(f"{module_no:02d}_*.yaml"))
    if not files:
        raise FileNotFoundError(f"config du module {module_no} introuvable")
    return engine_from_config(files[0])
