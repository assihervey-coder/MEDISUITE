"""Tests du moteur de fusion multimodale — la pièce maîtresse IA.

Couvre : pipeline complet, dégradation élégante (ADR-0018), déterminisme,
formes des blocs, 6 têtes, explicabilité, gestion d'erreurs.
"""
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from multimodal import FusionEngine, ModalityRegistry
from multimodal.core.cross_attention import CrossAttentionBlock, softmax
from multimodal.core.gated_fusion import GatedFusion
from multimodal.core.missing_modality import MissingModalityHandler
from multimodal.core.modality_encoder import TabularEncoder, TextEncoder, \
    GenomicEncoder, Signal1DEncoder
from multimodal.heads.heads import build_head

ENGINE = FusionEngine()


def _full_modalities():
    return {
        "tabulaire": {"features": [55, 1, 9.8, 132, 88, 24.5]},
        "imaging_2d": {"tensor": np.random.default_rng(0).normal(0.5, 0.2, (32, 32)).tolist()},
        "imaging_3d": {"tensor": np.random.default_rng(1).normal(0, 1, (8, 8, 4)).tolist()},
        "signal_1d": {"signal": np.random.default_rng(2).normal(0, 1, 500).tolist()},
        "texte": {"text": "nodule apical droit suspicion primaire suivi trois mois"},
        "genomique": {"sequence": "ATGGCAATTGCCGATTAGGCATCGGATCCGTAAGCTT"},
        "waveform": {"signal": np.random.default_rng(3).normal(0, 1, 400).tolist()},
    }


# ------------------------------------------------------------- pipeline complet

def test_inference_complete_7_modalites():
    r = ENGINE.infer(_full_modalities())
    assert r["confiance"] >= 0.99
    assert r["modalites_manquantes"]["complet"] is True
    assert abs(sum(r["modality_importance_pct"].values()) - 100) < 1.0


def test_une_seule_modalite_fonctionne():
    r = ENGINE.infer({"tabulaire": {"features": [1, 2, 3, 4]}})
    assert r["modalites_manquantes"]["absentes"]  # 6 absentes mais PAS d'erreur
    assert "prediction" in r


def test_determinisme_strict():
    a = ENGINE.infer({"tabulaire": {"features": [1, 2, 3]}})
    b = ENGINE.infer({"tabulaire": {"features": [1, 2, 3]}})
    assert a == b


def test_confiance_degradee_inferieure_nominale():
    r_full = ENGINE.infer(_full_modalities())
    r_poor = ENGINE.infer({"tabulaire": {"features": [1, 2, 3]}})
    assert r_poor["confiance"] < r_full["confiance"]
    # suggestion clinique : la biologie manquante est signalée
    actions = " ".join(ENGINE.infer({"imaging_2d": {"tensor": [[1, 2]]}})
                       ["modalites_manquantes"]["actions"])
    assert "tabulaire" in actions  # suggestion d'ajouter la biologie


def test_modalite_inconnue_rejetee():
    with pytest.raises(ValueError, match="inconnues"):
        ENGINE.infer({"telepathie": {"x": 1}})


def test_aucune_modalite_rejetee():
    with pytest.raises(ValueError):
        ENGINE.infer({})


# ------------------------------------------------------------- tâches (6 têtes)

@pytest.mark.parametrize("task,keys", [
    ("classification", {"classe", "probabilite", "seuil"}),
    ("multiclass", {"classe", "probabilites"}),
    ("multilabel", {"labels_actifs", "probabilites"}),
    ("regression", {"valeur"}),
    ("survival", {"score_risque", "lecture"}),
    ("segmentation", {"masque", "aire_estimee_pct"}),
])
def test_six_tetes(task, keys):
    r = ENGINE.infer({"tabulaire": {"features": [1, 2, 3]}}, task=task)
    assert keys <= set(r["prediction"].keys())


def test_tete_inconnue_rejetee():
    with pytest.raises(ValueError, match="tâche inconnue"):
        build_head("chimie_quantique", 32)


def test_multiclass_proba_somme_un():
    r = ENGINE.infer({"tabulaire": {"features": [5, 6, 7]}}, task="multiclass")
    assert abs(sum(r["prediction"]["probabilites"]) - 1.0) < 1e-6


def test_segmentation_grille_8x8():
    r = ENGINE.infer({"imaging_2d": {"tensor": [[1, 2]]}}, task="segmentation")
    assert len(r["prediction"]["masque"]) == 8
    assert 0 <= r["prediction"]["aire_estimee_pct"] <= 100


# ------------------------------------------------------------- blocs de base

def test_softmax_numeriquement_stable():
    x = np.array([1000.0, 1001.0])  # overflow sans stabilisation
    s = softmax(x)
    assert np.isfinite(s).all() and abs(s.sum() - 1) < 1e-9


def test_cross_attention_formes():
    block = CrossAttentionBlock(d_model=32)
    ctx, attn = block.forward(np.zeros(32), np.random.rand(16, 32))
    assert ctx.shape == (32,) and attn.shape == (16,)
    assert abs(attn.sum() - 1) < 1e-6  # distribution de probabilité


def test_gated_fusion_importance_normalisee():
    g = GatedFusion(["a", "b", "c"])
    fused, info = g.forward({"a": np.ones(8), "b": -np.ones(8)})
    assert fused.shape == (8,)
    assert abs(sum(info["importance"].values()) - 1) < 1e-9
    assert "c" not in info["importance"]  # absente = exclue, pas d'erreur


def test_missing_modality_handler():
    h = MissingModalityHandler(["a", "b", "c"])
    r = h.analyze(["a"])
    assert r.modalites_absentes == ["b", "c"] and not r.complet
    r_full = h.analyze(["a", "b", "c"])
    assert r_full.complet
    adj = MissingModalityHandler.confidence_adjustment(
        ["a"], {"a": 1.0, "b": 1.0, "c": 1.0})
    assert adj == pytest.approx(1 / 3)


# ------------------------------------------------------------- encodeurs

def test_encodeur_tabulaire_normalise():
    e = TabularEncoder(24)
    tokens, presence = e.encode({"features": [10, 20, 30]})
    assert tokens.shape == (1, 32) and presence.sum() == 1  # seq=1, d=32


def test_encodeur_texte_hashing():
    e = TextEncoder()
    tokens, _ = e.encode({"text": "mélanome nodulaire ulcéré"})
    assert tokens.shape == (16, 32)
    assert np.isfinite(tokens).all()


def test_encodeur_genomique_kmers():
    e = GenomicEncoder()
    tokens, _ = e.encode({"sequence": "ATGGCATGGCATGGC"})
    assert tokens.shape == (8, 32)
    assert abs(tokens.sum()) > 0  # les k-mers sont comptés


def test_encodeur_signal_fenetres():
    e = Signal1DEncoder()
    tokens, _ = e.encode({"signal": list(range(120))})
    assert tokens.shape == (12, 32)


def test_registre_dimensions():
    reg = ModalityRegistry()
    dims = reg.default_dimensions()
    assert set(dims) == {"imaging_2d", "imaging_3d", "signal_1d", "tabulaire",
                         "texte", "genomique", "waveform"}
    with pytest.raises(KeyError, match="inconnue"):
        reg.get("olfactive")
