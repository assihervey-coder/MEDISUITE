"""Factory : construit un FusionEngine depuis une config YAML (configs/*.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml

from .core.fusion_engine import FusionEngine

CONFIG_DIR = Path(__file__).resolve().parent / "configs"


def engine_from_config(config_path: str | Path) -> FusionEngine:
    """Construit un moteur depuis un YAML de module (01_imaging.yaml … 26_emergency).

    Clé optionnelle ``backend:`` (ADR 0022) : 'numpy' (défaut, aucune
    dépendance lourde), 'torch' (projection nn.Linear entraînable) ou 'monai'
    (prétraitement MONAI des images + projection torch). Lève ImportError
    documentée si le backend demandé n'est pas installé.
    """
    with open(config_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    engine = FusionEngine(
        d_model=int(cfg.get("d_model", 32)),
        task=cfg.get("task", "classification"),
        seed=int(cfg.get("seed", 42)),
    )
    backend = str(cfg.get("backend", "numpy")).lower()
    if backend != "numpy":
        from .core.backends import attach_backend
        attach_backend(engine, backend)
    return engine


def engine_for_module(module_no: int) -> FusionEngine:
    """Raccourci : module 8 → configs/08_cardiology.yaml."""
    files = sorted(CONFIG_DIR.glob(f"{module_no:02d}_*.yaml"))
    if not files:
        raise FileNotFoundError(f"config du module {module_no} introuvable")
    return engine_from_config(files[0])


def fusion_model_from_config(config_path: str | Path, heads: int = 1):
    """Construit un TorchFusionModel ENTRAÎNABLE (v0.3, ADR 0023).

    Requiert PyTorch (ImportError documentée sinon). Le modèle est initialisé
    depuis les poids NumPy du socle : équivalence numérique à l'init, divergence
    contrôlée dès le premier fit(). Entraînable : classification | multiclass |
    regression (survival/segmentation restent des gabarits NumPy).
    """
    from .core.torch_fusion import TorchFusionModel  # import paresseux torch
    return TorchFusionModel(engine_from_config(config_path), heads=heads)


def fusion_model_for_module(module_no: int, heads: int = 1):
    """Raccourci entraînable : module 8 → configs/08_cardiology.yaml."""
    files = sorted(CONFIG_DIR.glob(f"{module_no:02d}_*.yaml"))
    if not files:
        raise FileNotFoundError(f"config du module {module_no} introuvable")
    return fusion_model_from_config(files[0], heads=heads)
