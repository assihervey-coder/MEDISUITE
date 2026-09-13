"""FusionEngine — orchestrateur de bout en bout du pipeline multimodal.

Pipeline : validation → encodeurs → attention croisée par modalité →
gated fusion → tête de tâche → explicabilité + rapport de modalités manquantes.

Déterministe (graines fixes) : même entrée → même sortie, exigence de
reproductibilité clinique (docs/ml/validation-protocols.md).
"""
from __future__ import annotations

import numpy as np

from .cross_attention import CrossAttentionBlock
from .gated_fusion import GatedFusion
from .missing_modality import MissingModalityHandler
from .modality_encoder import build_encoders
from .registry import ModalityRegistry
from ..heads.heads import build_head


class FusionEngine:
    """Moteur de fusion multimodal résilient aux modalités manquantes."""

    def __init__(self, dims: dict[str, tuple[int, int]] | None = None,
                 d_model: int = 32, task: str = "classification",
                 seed: int = 42) -> None:
        self.registry = ModalityRegistry()
        self.dims = dims or self.registry.default_dimensions()
        self.d_model = d_model
        self.task = task
        self.encoders = build_encoders(self.dims, d_model)
        self.attention = {m: CrossAttentionBlock(d_model, seed=seed + i)
                          for i, m in enumerate(self.dims)}
        self.gated = GatedFusion(list(self.dims), seed=seed)
        self.head = build_head(task, d_model)
        self.handler = MissingModalityHandler(list(self.dims))
        # token global appris (graine) — requête initiale de l'attention
        rng = np.random.default_rng(seed)
        self.global_query = rng.normal(0, 0.05, d_model)

    def infer(self, modalities: dict, task: str | None = None) -> dict:
        """modalities : {nom_modalité: payload}. Retour structuré complet."""
        provided = list(modalities.keys())
        unknown = [m for m in provided if m not in self.encoders]
        if unknown:
            raise ValueError(f"modalités inconnues : {unknown} — "
                             f"connues : {sorted(self.encoders)}")
        report = self.handler.analyze(provided)
        if not report.modalites_presentes:
            raise ValueError("aucune modalité exploitable")

        # 1. encodage des modalités présentes
        encoded = {m: self.encoders[m].encode(modalities[m])
                   for m in report.modalites_presentes}

        # 2. requête globale → attention croisée avec CHAQUE modalité
        query = self.global_query
        summaries = {}
        attn_mass = {}
        for m, (tokens, _presence) in encoded.items():
            ctx, attn = self.attention[m].forward(query, tokens)
            summaries[m] = ctx
            attn_mass[m] = float(attn.sum())  # masse totale ≈ 1 par modalité

        # 3. fusion gated + importance
        fused, gate_info = self.gated(summaries)

        # 4. recalibrage de confiance selon modalités manquantes (ADR-0018)
        all_weights = {m: self.gated._sigmoid(g)
                       for m, g in self.gated.gates.items()}
        adj = self.handler.confidence_adjustment(
            report.modalites_presentes, all_weights)

        # 5. tête de tâche
        task = task or self.task
        head = self.head if task == self.task else build_head(task, self.d_model)
        prediction = head(fused)

        # 6. importance des modalités (portes × masse d'attention) — ADR-0015
        importance = {m: round(100 * gate_info["importance"][m], 1)
                      for m in summaries}

        return {
            "task": task,
            "prediction": prediction,
            "confiance": round(min(1.0, 0.5 + 0.5 * adj), 3),
            "modalites_manquantes": report.to_dict(),
            "modality_importance_pct": importance,
            "detail": {"d_model": self.d_model,
                       "modalites_encodees": len(summaries),
                       "gates": {k: round(v, 3)
                                 for k, v in gate_info["gates"].items()}},
        }
