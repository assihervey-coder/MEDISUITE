"""Têtes de sortie multi-tâches (ADR-0019) — 6 familles sur tronc partagé."""
from __future__ import annotations

import numpy as np

from ..core.cross_attention import softmax


class BinaryHead:
    """Classification binaire : sigmoid(w·fused + b)."""

    def __init__(self, d_model: int, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.w = rng.normal(0, 0.5, d_model)
        self.b = 0.0

    def forward(self, fused: np.ndarray) -> dict:
        logit = float(self.w @ fused + self.b)
        p = float(1.0 / (1.0 + np.exp(-logit)))
        return {"classe": 1 if p >= 0.5 else 0,
                "probabilite": round(p, 4),
                "seuil": 0.5}

    __call__ = forward


class MulticlassHead:
    """Classification K classes : softmax."""

    def __init__(self, d_model: int, n_classes: int = 4, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.5, (d_model, n_classes))

    def forward(self, fused: np.ndarray) -> dict:
        probs = softmax(fused @ self.W)
        return {"classe": int(np.argmax(probs)),
                "probabilites": [round(float(p), 4) for p in probs]}

    __call__ = forward


class MultilabelHead:
    """Multi-label : sigmoid indépendant par étiquette."""

    def __init__(self, d_model: int, n_labels: int = 5, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.5, (d_model, n_labels))

    def forward(self, fused: np.ndarray) -> dict:
        p = 1.0 / (1.0 + np.exp(-(fused @ self.W)))
        return {"labels_actifs": [int(i) for i in np.where(p >= 0.5)[0]],
                "probabilites": [round(float(x), 4) for x in p]}

    __call__ = forward


class RegressionHead:
    """Régression : valeur continue (ex. DFG prédit, survie en mois)."""

    def __init__(self, d_model: int, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.w = rng.normal(0, 0.5, d_model)

    def forward(self, fused: np.ndarray) -> dict:
        return {"valeur": round(float(self.w @ fused), 4)}

    __call__ = forward


class SurvivalHead:
    """Risque de Cox simplifié : score de risque relatif exp(w·fused)."""

    def __init__(self, d_model: int, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.w = rng.normal(0, 0.3, d_model)

    def forward(self, fused: np.ndarray) -> dict:
        risk = float(np.exp(self.w @ fused))
        return {"score_risque": round(risk, 4),
                "lecture": ">1 risque accru, <1 protecteur"}

    __call__ = forward


class SegmentationHead:
    """Segmentation : grille de probabilités dérivée du tronc (gabarit)."""

    def __init__(self, d_model: int, grid: int = 8, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.4, (d_model, grid * grid))
        self.grid = grid

    def forward(self, fused: np.ndarray) -> dict:
        g = (fused @ self.W).reshape(self.grid, self.grid)
        p = 1.0 / (1.0 + np.exp(-g))
        return {"masque": [[round(float(v), 3) for v in row] for row in p],
                "aire_estimee_pct": round(float((p >= 0.5).mean() * 100), 1)}

    __call__ = forward


def build_head(task: str, d_model: int, n_classes: int = 4):
    """Fabrique de tête selon la tâche (registry/factory)."""
    mapping = {"classification": BinaryHead,
               "multiclass": lambda d: MulticlassHead(d, n_classes),
               "multilabel": lambda d: MultilabelHead(d),
               "regression": RegressionHead,
               "survival": SurvivalHead,
               "segmentation": lambda d: SegmentationHead(d)}
    if task not in mapping:
        raise ValueError(f"tâche inconnue '{task}' — {sorted(mapping)}")
    head = mapping[task](d_model)
    return head
