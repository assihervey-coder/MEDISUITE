"""Backends de calcul des encodeurs — NumPy (défaut), PyTorch, MONAI (ADR 0022).

Architecture : le moteur de fusion v0.1 est NumPy-déterministe, testable sans
dépendances lourdes (exigence IEC 62304 : chaîne de test reproductible). La
v0.2 introduit des backends entraînables optionnels à interface identique :

- ``torch``  : la projection statique (tokens @ P) est remplacée par un
  ``torch.nn.Linear`` dont les poids sont *copiés depuis la matrice stable P*.
  À l'initialisation, la sortie est donc numériquement identique au socle
  NumPy (au flottement float64 → float32) : les tests de régression v0.1
  restent valides, et l'entraînement peut reprendre depuis ce point.
- ``monai``  : prétraitement d'image MONAI canonique (EnsureChannelFirst,
  ScaleIntensity, Resize) inséré AVANT la tokenisation des encodeurs
  ``imaging_2d`` / ``imaging_3d``, puis projection torch.

Import paresseux : torch/monai ne sont requis QUE si un backend explicite est
demandé via la config (``backend: torch``) — le moteur et les tests numpy
passent sur une machine sans ces dépendances.
"""
from __future__ import annotations

import hashlib

import numpy as np

from .modality_encoder import BaseEncoder, Image2DEncoder, _stable_projection

IMAGE_MODALITIES = {"imaging_2d", "imaging_3d"}


def _require_torch():
    try:
        import torch  # noqa: PLC0415 — import paresseux volontaire
    except ImportError as exc:  # pragma: no cover — dépend de l'env
        raise ImportError(
            "backend 'torch' demandé mais PyTorch est absent. "
            "Installation CPU : pip install torch --index-url "
            "https://download.pytorch.org/whl/cpu (voir ai/requirements.txt)"
        ) from exc
    return torch


def _require_monai():
    _require_torch()
    try:
        import monai  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "backend 'monai' demandé mais MONAI est absent. "
            "Installation : pip install monai (voir ai/requirements.txt)"
        ) from exc
    return monai


class TorchProjector:
    """Projection entraînable torch.nn.Linear, initialisée depuis P stable.

    Garantie v0.2 : ``project(tokens) == tokens @ P`` à l'init (écart float32),
    puis devient différent dès la première mise à jour de gradient — le backend
    est donc un sur-ensemble strict du comportement NumPy.
    """

    def __init__(self, name: str, seq_len: int, feature_dim: int, d_model: int) -> None:
        torch = _require_torch()
        self._torch = torch
        # graine déterministe dérivée du nom (même politique que _stable_projection)
        seed = int(hashlib.sha256(("torch:" + name).encode()).hexdigest()[:8], 16)
        torch.manual_seed(seed)
        # float64 dès la construction : copie exacte de P (float64) sans cast
        self.linear = torch.nn.Linear(feature_dim, d_model, bias=False,
                                      dtype=torch.float64)
        with torch.no_grad():
            self.linear.weight.copy_(torch.from_numpy(_stable_projection(
                name, seq_len, feature_dim, d_model).T))

    def project(self, tokens: np.ndarray) -> np.ndarray:
        with self._torch.no_grad():
            out = self.linear(self._torch.from_numpy(np.ascontiguousarray(tokens)))
        return out.numpy()


class MonaiImagePreproc:
    """Prétraitement MONAI canonique pour images 2D/3D (déterministe).

    Pipeline : EnsureChannelFirst → ScaleIntensity → Resize(spatial_size).
    Le resize cible 64×64 (2D) ou 32×32×32 (3D) — taille indépendante de
    l'acquisition, prérequis de batch homogène avant tokenisation par patches.
    """

    def __init__(self, three_d: bool) -> None:
        monai = _require_monai()
        import torch  # noqa: PLC0415
        spatial = (32, 32, 32) if three_d else (64, 64)
        self.transform = monai.transforms.Compose([
            monai.transforms.EnsureChannelFirst(channel_dim="no_channel"),
            monai.transforms.ScaleIntensity(),
            monai.transforms.Resize(spatial_size=spatial),
        ])
        self._torch = torch

    def __call__(self, tensor: np.ndarray) -> np.ndarray:
        import torch  # noqa: PLC0415
        t = self.transform(torch.from_numpy(np.asarray(tensor, dtype=np.float32)))
        return t.numpy()


def _wrap_monai_tokens(encoder: BaseEncoder) -> None:
    """Insère le prétraitement MONAI dans la tokenisation d'un encodeur image."""
    original = encoder._to_tokens
    preproc = MonaiImagePreproc(three_d="3d" in encoder.name)

    def with_monai(payload):
        tensor = payload.get("tensor", payload) if isinstance(payload, dict) else payload
        arr = np.asarray(tensor, dtype=float)
        if arr.size == 0:  # payload vide : comportement NumPy inchangé
            return original(payload)
        preprocessed = preproc(arr)
        return original({"tensor": preprocessed} if isinstance(payload, dict)
                        else preprocessed)

    encoder._to_tokens = with_monai  # type: ignore[method-assign]


def attach_backend(engine, backend: str = "numpy"):
    """Branche un backend de projection sur tous les encodeurs du moteur.

    backend ∈ {'numpy', 'torch', 'monai'} — 'numpy' est un no-op explicite.
    Retourne le moteur (chaînable). Lève ImportError avec instruction
    d'installation si torch/monai sont absents.
    """
    backend = (backend or "numpy").lower()
    if backend == "numpy":
        return engine
    if backend not in {"torch", "monai"}:
        raise ValueError(f"backend inconnu : {backend!r} — attendus : numpy|torch|monai")

    _require_torch()  # valide la disponibilité AVANT de muter les encodeurs
    if backend == "monai":
        _require_monai()

    for enc in engine.encoders.values():
        proj = TorchProjector(enc.name, enc.seq_len, enc.feature_dim, enc.d_model).project
        enc.project = proj  # type: ignore[method-assign]
        enc._backend = backend  # type: ignore[attr-defined]
        if backend == "monai" and enc.name in IMAGE_MODALITIES:
            _wrap_monai_tokens(enc)
    return engine


def backend_of(engine) -> str:
    """Backend effectivement branché sur le moteur ('numpy' par défaut)."""
    first = next(iter(engine.encoders.values()), None)
    return getattr(first, "_backend", "numpy") if first is not None else "numpy"
