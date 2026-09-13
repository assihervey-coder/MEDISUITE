__version__ = "0.3.0"
"""Fusion multimodale cross-attention, résiliente aux modalités manquantes.

Socle NumPy déterministe (défaut, IEC 62304) + backends torch/monai (ADR 0022)
+ modèle de fusion ENTRAÎNABLE de bout en bout (ADR 0023).
"""
from .core.fusion_engine import FusionEngine  # noqa: F401
from .core.registry import ModalityRegistry  # noqa: F401
