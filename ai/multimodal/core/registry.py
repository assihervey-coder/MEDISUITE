"""Registre des modalités : dimensions d'entrée, encodages, configuration.

Source de vérité partagée entre le moteur de fusion (ai/multimodal) et la
multimodal-gateway (services/multimodal-gateway).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModalitySpec:
    name: str
    seq_len: int          # longueur de séquence de tokens après encodage
    feature_dim: int      # dimension des features par token avant projection
    description: str = ""


DEFAULT_SPEC: dict[str, ModalitySpec] = {
    "imaging_2d": ModalitySpec("imaging_2d", 16, 16, "images 2D (fond d'œil, dermoscopie)"),
    "imaging_3d": ModalitySpec("imaging_3d", 8, 16, "volumes 3D (IRM, scanner)"),
    "signal_1d": ModalitySpec("signal_1d", 12, 8, "signaux (ECG 12 dérivations)"),
    "tabulaire": ModalitySpec("tabulaire", 1, 24, "données cliniques/biologie"),
    "texte": ModalitySpec("texte", 16, 16, "comptes-rendus, notes"),
    "genomique": ModalitySpec("genomique", 8, 16, "profils génomiques (k-mers)"),
    "waveform": ModalitySpec("waveform", 12, 8, "waveforms (CTG, EEG)"),
}


class ModalityRegistry:
    """Accès aux spécifications et dimensions par défaut de projection."""

    def __init__(self, specs: dict[str, ModalitySpec] | None = None,
                 d_model: int = 32) -> None:
        self.specs = specs or dict(DEFAULT_SPEC)
        self.d_model = d_model

    @classmethod
    def default_dimensions(cls) -> dict[str, tuple[int, int]]:
        """{modalité: (seq_len, feature_dim)} — utilisé par la gateway et les tests."""
        return {name: (s.seq_len, s.feature_dim)
                for name, s in DEFAULT_SPEC.items()}

    def get(self, name: str) -> ModalitySpec:
        if name not in self.specs:
            raise KeyError(f"modalité inconnue '{name}' — "
                           f"connues : {sorted(self.specs)}")
        return self.specs[name]
