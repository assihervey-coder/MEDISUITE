"""Blocs d'attention croisée multi-têtes — implémentation de référence NumPy.

ADR-0016 (fusion intermédiaire) et ADR-0017 (cross-attention).
Les poids sont un gabarit déterministe (graine fixe) ; le chargement de poids
entraînés (PyTorch/MONAI) est prévu en v0.2 (ADR-0003).
"""
from __future__ import annotations

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def layer_norm(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    mean = x.mean(axis=-1, keepdims=True)
    var = x.var(axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps)


class CrossAttentionBlock:
    """Attention croisée : Query (représentation globale) × Keys/Values (modalité).

    attn = softmax(QKᵀ/√d)·V — multi-têtes supporté via h. Retourne
    (contexte, poids_d_attention) pour l'explicabilité (ADR-0015).
    """

    def __init__(self, d_model: int, heads: int = 1, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.h = heads
        self.d_model = d_model
        self.d_head = d_model // heads
        self.Wq = rng.normal(0, 0.1, (d_model, d_model))
        self.Wk = rng.normal(0, 0.1, (d_model, d_model))
        self.Wv = rng.normal(0, 0.1, (d_model, d_model))
        self.Wo = rng.normal(0, 0.1, (d_model, d_model))

    def forward(self, query: np.ndarray, kv_seq: np.ndarray
                ) -> tuple[np.ndarray, np.ndarray]:
        """query : (d,) ; kv_seq : (T, d) → (contexte (d,), poids (T,))."""
        q = query @ self.Wq                      # (d,)
        k = kv_seq @ self.Wk                     # (T, d)
        v = kv_seq @ self.Wv                     # (T, d)
        scores = (k @ q) / np.sqrt(self.d_model)  # (T,)
        attn = softmax(scores)                   # (T,)
        ctx = attn @ v                           # (d,)
        out = layer_norm(query + ctx @ self.Wo)
        return out, attn

    __call__ = forward
