"""Encodeurs de modalités — 7 familles, implémentation NumPy déterministe.

Chaque encodeur transforme l'entrée brute (dict ou array) en une séquence
de tokens (seq_len × feature_dim) projetée vers d_model. La projection est
un gabarit de poids fixe (graine) — remplacée par des poids entraînés en v0.2.
"""
from __future__ import annotations

import hashlib

import numpy as np


def _stable_projection(name: str, seq_len: int, feature_dim: int,
                       d_model: int) -> np.ndarray:
    """Matrice de projection déterministe par modalité (graine dérivée du nom).

    Forme (feature_dim, d_model) : tokens (seq_len, feature_dim) @ P →
    (seq_len, d_model)."""
    seed = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    return rng.normal(0, 0.3, (feature_dim, d_model))


class BaseEncoder:
    """Encodeur générique : normalise l'entrée → tokens → projection d_model."""

    def __init__(self, name: str, seq_len: int, feature_dim: int,
                 d_model: int = 32) -> None:
        self.name = name
        self.seq_len = seq_len
        self.feature_dim = feature_dim
        self.d_model = d_model
        self.P = _stable_projection(name, seq_len, feature_dim, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        raise NotImplementedError

    def project(self, tokens: np.ndarray) -> np.ndarray:
        """Projection (seq, feature_dim) → (seq, d_model).

        Point d'injection des backends entraînables (torch/monai — ADR 0022) :
        la projection statique déterministe ``tokens @ self.P`` reste le
        comportement par défaut, reproductible sans dépendances lourdes."""
        return tokens @ self.P

    def encode(self, payload) -> tuple[np.ndarray, np.ndarray]:
        """→ (tokens projetés (seq, d_model), présence (seq,) — 1 partout ici)."""
        tokens = self._to_tokens(payload).reshape(-1)[:self.seq_len * self.feature_dim]
        tokens = np.pad(tokens, (0, self.seq_len * self.feature_dim - len(tokens)))
        tokens = tokens.reshape(self.seq_len, self.feature_dim)
        return self.project(tokens), np.ones(self.seq_len)

class TabularEncoder(BaseEncoder):
    """Données cliniques/biologiques : vecteur plat normalisé min-max."""

    def __init__(self, feature_dim: int, d_model: int = 32) -> None:
        super().__init__("tabulaire", 1, feature_dim, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        vals = payload.get("features", []) if isinstance(payload, dict) else payload
        arr = np.asarray(vals, dtype=float).ravel()
        std = arr.std() or 1.0
        return ((arr - arr.mean()) / std).reshape(1, -1)


class Image2DEncoder(BaseEncoder):
    """Image 2D : grille NxN → tokens par patch (moyenne par bloc)."""

    def __init__(self, d_model: int = 32) -> None:
        super().__init__("imaging_2d", 16, 16, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        tensor = np.asarray(payload.get("tensor", []), dtype=float) \
            if isinstance(payload, dict) else np.asarray(payload, dtype=float)
        if tensor.size == 0:
            return np.zeros((self.seq_len, self.feature_dim))
        # normalisation par canaux puis aplat
        t = (tensor - tensor.mean()) / (tensor.std() or 1.0)
        return t.reshape(1, -1)


class Image3DEncoder(Image2DEncoder):
    """Volume 3D : même pipeline, slices = batch implicite."""

    def __init__(self, d_model: int = 32) -> None:
        BaseEncoder.__init__(self, "imaging_3d", 8, 16, d_model)


class Signal1DEncoder(BaseEncoder):
    """Signal 1D (ECG) : fenêtrage RMS réduit à seq_len points."""

    def __init__(self, d_model: int = 32) -> None:
        super().__init__("signal_1d", 12, 8, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        vals = payload.get("signal", []) if isinstance(payload, dict) else payload
        arr = np.asarray(vals, dtype=float).ravel()
        if arr.size == 0:
            return np.zeros((self.seq_len, self.feature_dim))
        if arr.size < self.seq_len:
            arr = np.pad(arr, (0, self.seq_len - arr.size))
        chunks = np.array_split(arr[:arr.size // self.seq_len * self.seq_len],
                                self.seq_len)
        rms = np.array([np.sqrt((c ** 2).mean()) for c in chunks])
        return ((rms - rms.mean()) / (rms.std() or 1.0)).reshape(-1, 1) \
            @ np.ones((1, self.feature_dim))


class TextEncoder(BaseEncoder):
    """Texte : hashing trick (sac de n-grams signés) — aucun modèle externe requis."""

    def __init__(self, d_model: int = 32) -> None:
        super().__init__("texte", 16, 16, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        text = payload.get("text", "") if isinstance(payload, dict) else str(payload)
        words = text.lower().split()
        tokens = np.zeros((self.seq_len, self.feature_dim))
        for i, w in enumerate(words[:self.seq_len]):
            h = int(hashlib.sha256(w.encode()).hexdigest()[:8], 16)
            tokens[i % self.seq_len, h % self.feature_dim] += 1.0
            tokens[i % self.seq_len, (h >> 8) % self.feature_dim] -= 0.5
        return tokens.reshape(1, -1)  # (1, seq*feat)


class GenomicEncoder(BaseEncoder):
    """Génomique : comptage de k-mers (k=3) normalisé."""

    def __init__(self, d_model: int = 32) -> None:
        super().__init__("genomique", 8, 16, d_model)

    def _to_tokens(self, payload) -> np.ndarray:
        seq = payload.get("sequence", "") if isinstance(payload, dict) else ""
        seq = "".join(c for c in str(seq).upper() if c in "ACGT")
        counts = np.zeros(16)
        for i in range(max(0, len(seq) - 2)):
            idx = sum("ACGT".find(c) * (4 ** j)
                      for j, c in enumerate(seq[i:i + 3][::-1])) % 16
            counts[idx] += 1
        counts = counts / (counts.sum() or 1.0)
        return counts.reshape(1, -1)


class WaveformEncoder(Signal1DEncoder):
    """Waveform (CTG, EEG) — même fenêtrage RMS que le signal 1D."""

    def __init__(self, d_model: int = 32) -> None:
        BaseEncoder.__init__(self, "waveform", 12, 8, d_model)


def build_encoders(dims: dict[str, tuple[int, int]],
                   d_model: int = 32) -> dict[str, BaseEncoder]:
    """Fabrique les 7 encodeurs à partir des dimensions du registre."""
    classes = {"tabulaire": TabularEncoder, "imaging_2d": Image2DEncoder,
               "imaging_3d": Image3DEncoder, "signal_1d": Signal1DEncoder,
               "texte": TextEncoder, "genomique": GenomicEncoder,
               "waveform": WaveformEncoder}
    out = {}
    for name, (seq_len, feature_dim) in dims.items():
        cls = classes[name]
        if cls in (TabularEncoder,):
            out[name] = cls(feature_dim, d_model)
        else:
            enc = cls.__new__(cls)
            BaseEncoder.__init__(enc, name, seq_len, feature_dim, d_model)
            out[name] = enc
    return out
