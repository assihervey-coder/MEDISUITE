"""Tests des backends torch/monai (ADR 0022).

Contrats vérifiés :
- numpy reste le défaut : aucun import torch requis, comportement inchangé ;
- torch : sortie identique au socle NumPy à l'initialisation (copie exacte de
  P en float64) + déterminisme sur appels répétés ;
- monai : prétraitement image inséré (backend tracé) ;
- factory : backend inconnu rejeté.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from multimodal.core.backends import attach_backend, backend_of
from multimodal.core.modality_encoder import _stable_projection
from multimodal.factory import engine_for_module


def test_numpy_backend_par_defaut():
    engine = engine_for_module(1)
    assert backend_of(engine) == "numpy"


def test_attach_backend_inconnu_rejete():
    engine = engine_for_module(1)
    with pytest.raises(ValueError, match="backend inconnu"):
        attach_backend(engine, "jax")


def test_torch_equivalence_numpy_a_l_init():
    """Sans torch installé : skip — le socle NumPy reste la référence v0.1.

    Équivalence vérifiée au niveau des encodeurs (seul point branché par le
    backend) : poids du nn.Linear copiés depuis P → tokens identiques."""
    pytest.importorskip("torch", reason="PyTorch absent (option v0.2)")
    engine = engine_for_module(1)
    img_payload = {"tensor": np.random.default_rng(0).normal(0, 1, (64, 64))}
    tab_payload = {"features": [0.1, 0.5, 0.9]}
    enc_img, enc_tab = engine.encoders["imaging_2d"], engine.encoders["tabulaire"]
    base_img = enc_img.encode(img_payload)[0]
    base_tab = enc_tab.encode(tab_payload)[0]

    attach_backend(engine, "torch")
    assert backend_of(engine) == "torch"

    torch_img = enc_img.encode(img_payload)[0]
    torch_tab = enc_tab.encode(tab_payload)[0]
    np.testing.assert_allclose(torch_img, base_img, rtol=1e-6, atol=1e-8)
    np.testing.assert_allclose(torch_tab, base_tab, rtol=1e-6, atol=1e-8)


def test_torch_pipeline_identique_apres_branchement():
    """Le résultat complet d'inférence (dict arrondi) est inchangé après
    branchement torch — garantie de continuité des tests de régression."""
    pytest.importorskip("torch")
    engine = engine_for_module(1)
    payload = {
        "imaging_2d": {"tensor": np.random.default_rng(0).normal(0.5, 0.2, (32, 32)).tolist()},
        "tabulaire": {"features": [55, 1, 9.8, 132, 88, 24.5]},
    }
    before = engine.infer(dict(payload))
    attach_backend(engine, "torch")
    after = engine.infer(dict(payload))
    assert before == after


def test_torch_determinisme():
    pytest.importorskip("torch")
    engine = engine_for_module(2)
    attach_backend(engine, "torch")
    payload = {"imaging_2d": np.random.default_rng(3).normal(size=(32, 32))}
    r1 = engine.infer(dict(payload))["prediction"]
    r2 = engine.infer(dict(payload))["prediction"]
    np.testing.assert_array_equal(np.asarray(r1), np.asarray(r2))


def test_monai_pretraitement_image():
    monai = pytest.importorskip("monai", reason="MONAI absent (option v0.2)")
    engine = engine_for_module(1)
    attach_backend(engine, "monai")
    assert backend_of(engine) == "monai"
    assert monai.__version__
    out = engine.infer({
        "imaging_2d": {"tensor": np.random.default_rng(5).normal(size=(100, 128)).tolist()},
    })
    assert out["prediction"] is not None


def test_stable_projection_dtype_et_forme():
    p = _stable_projection("imaging_2d", 16, 16, 32)
    assert p.shape == (16, 32)
    assert p.dtype == np.float64
