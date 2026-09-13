"""Explicabilité : importance des modalités et visualisation d'attention.

Feuille de route (ADR-0015) : SHAP/GradCAM natifs en v0.2 côté PyTorch ;
la version NumPy expose déjà l'importance dérivée des portes × attention,
suffisante pour l'affichage clinique « pourquoi cette prédiction ? ».
"""
from __future__ import annotations

import numpy as np


def modality_importance(gates: dict[str, float],
                        attention_mass: dict[str, float] | None = None) -> dict:
    """Importance en % par modalité = poids de porte × masse d'attention."""
    mass = attention_mass or {m: 1.0 for m in gates}
    raw = {m: gates[m] * mass.get(m, 1.0) for m in gates}
    total = sum(raw.values()) or 1.0
    return {m: round(100 * v / total, 1) for m, v in raw.items()}


def attention_summary(attn: np.ndarray, tokens_labels: list[str] | None = None
                      ) -> dict:
    """Résumé d'une distribution d'attention (T,) : top tokens contributifs."""
    t = attn.shape[0]
    labels = tokens_labels or [f"token_{i}" for i in range(t)]
    order = np.argsort(attn)[::-1]
    return {"top_tokens": [{"label": labels[i], "poids": round(float(attn[i]), 3)}
                            for i in order[:5]],
            "entropie": round(float(-(attn * np.log(attn + 1e-9)).sum()), 3),
            "lecture": ("attention concentrée" if
                        (attn.max() > 0.5) else "attention diffuse")}
