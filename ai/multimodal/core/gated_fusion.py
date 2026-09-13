"""Fusion gated : pondération des résumés de modalités (ADR-0016).

Les portes (gates) sigmoid sont un gabarit déterministe ; l'importance des
modalités retournée est dérivée des portes × masse d'attention — utilisée
par l'explicabilité (ADR-0015) et exposée au clinicien.
"""
from __future__ import annotations

import numpy as np


class GatedFusion:
    """Somme pondérée par portes : fused = Σ_i sigmoid(g_i) · summary_i."""

    def __init__(self, modalities: list[str], seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.modalities = list(modalities)
        # biais initial positif → chaque modalité contribue au départ
        self.gates: dict[str, float] = {
            m: float(rng.uniform(0.4, 1.2)) for m in self.modalities}

    def forward(self, summaries: dict[str, np.ndarray]) -> tuple[np.ndarray, dict]:
        """summaries : {modalité: vecteur (d,)} → (fused (d,), importance)."""
        present = [m for m in self.modalities if m in summaries]
        if not present:
            raise ValueError("aucune modalité présente à fusionner")
        weights = {m: self._sigmoid(self.gates[m]) for m in present}
        total = sum(weights.values())
        fused = sum(weights[m] * summaries[m] for m in present)
        importance = {m: weights[m] / total for m in present}
        return fused, {"gates": weights, "importance": importance}

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    __call__ = forward
