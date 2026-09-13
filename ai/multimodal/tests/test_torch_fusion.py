"""Tests de la fusion torch entraînable (v0.3, ADR 0023).

Contrats vérifiés :
- équivalence NumPy à l'initialisation (poids copiés — pattern ADR 0022
  étendu au tronc : attention, portes, requête, tête) ;
- gradients atteignent TOUS les blocs entraînables ;
- fit() : perte décroissante + apprentissage réel sur dataset synthétique
  linéairement séparable ;
- checkpoints : round-trip save/load sans divergence ;
- modalités manquantes : inférence dégradée cohérente (ADR-0018) ;
- garde-fous : tâches non entraînables rejetées (survival/segmentation),
  heads invalide, incohérence tâche/tête.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

torch = pytest.importorskip("torch", reason="PyTorch absent (option v0.3)")

from multimodal.core.torch_fusion import (  # noqa: E402
    TorchFusionModel, TorchTaskHead, TRAINABLE_TASKS)
from multimodal.factory import engine_for_module  # noqa: E402
from multimodal.heads.heads import MulticlassHead  # noqa: E402


def _payload(rng: np.random.Generator | None = None) -> dict:
    rng = rng or np.random.default_rng(0)
    return {
        "imaging_2d": {"tensor": rng.normal(0.5, 0.2, (32, 32)).tolist()},
        "tabulaire": {"features": [55, 1, 9.8, 132, 88, 24.5]},
    }


def _samples_separables(n: int = 40) -> list:
    """tabulaire décide (seuil 60 ans), imagerie = bruit pur (informatif nul)."""
    rng = np.random.default_rng(7)
    out = []
    for _ in range(n):
        feat = [float(rng.uniform(20, 90)), float(rng.integers(0, 2)), 9.9]
        img = rng.normal(0.5, 0.2, (16, 16)).tolist()
        out.append(({"tabulaire": {"features": feat},
                     "imaging_2d": {"tensor": img}}, 1 if feat[0] > 60 else 0))
    return out


# ── équivalence à l'initialisation ───────────────────────────────────────────

def test_equivalence_numpy_a_l_init():
    """À poids copiés, predict() == engine.infer() (au flottement/arrondis)."""
    engine = engine_for_module(1)
    pl = _payload()
    ref = engine.infer(dict(pl))
    model = TorchFusionModel(engine)
    out = model.predict(dict(pl))
    assert out["task"] == ref["task"]
    assert out["prediction"]["classe"] == ref["prediction"]["classe"]
    assert out["prediction"]["probabilite"] == pytest.approx(
        ref["prediction"]["probabilite"], abs=1.5e-4)
    assert out["confiance"] == ref["confiance"]
    for m, v in ref["modality_importance_pct"].items():
        assert out["modality_importance_pct"][m] == pytest.approx(v, abs=0.15)
    assert out["modalites_manquantes"] == ref["modalites_manquantes"]
    assert out["detail"]["backend"] == "torch_fusion"


def test_equivalence_numerique_fused_rtol_1e6():
    """Le tenseur fused torch est identique au fused NumPy (rtol 1e-6)."""
    engine = engine_for_module(1)
    pl = _payload()
    # socle NumPy : encodage → attention → gated (pipeline interne public)
    encoded = {m: engine.encoders[m].encode(pl[m])[0]
               for m in ("imaging_2d", "tabulaire")}
    summaries = {}
    for m, tokens in encoded.items():
        ctx, _ = engine.attention[m].forward(engine.global_query, tokens)
        summaries[m] = ctx
    fused_np, _info = engine.gated(summaries)

    model = TorchFusionModel(engine)
    with torch.no_grad():
        tok = {m: torch.tensor(model._tokenize(m, pl[m]), dtype=torch.float64)
               for m in ("imaging_2d", "tabulaire")}
        fused_t, _w, _imp, _a = model._fuse(["imaging_2d", "tabulaire"], tok)
    np.testing.assert_allclose(fused_t.numpy(), fused_np, rtol=1e-6, atol=1e-9)


def test_multi_tetes_h2_fonctionne():
    """heads=2 diverge du socle (attention réellement multi-têtes) mais reste
    cohérente : sortie structurée complète, importance sommant à ~100 %."""
    engine = engine_for_module(1)
    model = TorchFusionModel(engine, heads=2)
    out = model.predict(_payload())
    assert out["detail"]["heads"] == 2
    assert sum(out["modality_importance_pct"].values()) == pytest.approx(100, abs=0.3)


def test_heads_invalide_rejete():
    engine = engine_for_module(1)
    with pytest.raises(ValueError, match="diviser d_model"):
        TorchFusionModel(engine, heads=7)   # 32 % 7 ≠ 0


# ── gradients ────────────────────────────────────────────────────────────────

def test_gradients_atteignent_tous_les_blocs_actifs():
    """Toute modalité PRÉSENTE contribue au graphe (projecteur + attention) ;
    portes, requête globale et tête reçoivent des gradients finis. Les blocs
    des modalités absentes n'ont pas de gradient (comportement attendu —
    gradient épars, ADR-0018)."""
    engine = engine_for_module(1)
    model = TorchFusionModel(engine)
    pl = _payload()
    presentes = ("imaging_2d", "tabulaire")
    tok = {m: torch.tensor(model._tokenize(m, pl[m]), dtype=torch.float64)
           for m in presentes}
    fused, _w, _imp, _a = model._fuse(list(presentes), tok)
    loss = model.head(fused)["logit"].sum()
    loss.backward()
    for nom, param in model.named_parameters():
        prefixes = tuple(f"{bloc}.{m}." for bloc in ("projectors", "attention")
                         for m in presentes)
        bloc_actif = (nom.startswith(prefixes)
                      or nom in ("gates", "global_query")
                      or nom.startswith("head."))
        if bloc_actif:
            assert param.grad is not None, f"pas de gradient : {nom}"
            assert torch.isfinite(param.grad).all(), f"gradient non fini : {nom}"
        else:
            assert param.grad is None, f"gradient inattendu (bloc inactif) : {nom}"


# ── entraînement ─────────────────────────────────────────────────────────────

def test_fit_perte_decroissante():
    model = TorchFusionModel(engine_for_module(1))
    hist = model.fit(_samples_separables(), epochs=30)
    assert len(hist) == 30
    assert hist[-1] < hist[0], "la perte doit décroître sur le dataset séparable"
    assert all(np.isfinite(hist)), "perte non finie — entraînement instable"


def test_fit_apprentissage_reel():
    """Après fit, accuracy parfaite sur le train (dataset trivialement séparable)."""
    samples = _samples_separables()
    model = TorchFusionModel(engine_for_module(1))
    model.fit(samples, epochs=200, lr=2e-2)
    bonnes = sum(1 for pl, y in samples
                 if model.predict(pl)["prediction"]["classe"] == y)
    assert bonnes == len(samples), "accuracy < 100 % sur dataset séparable"


def test_fit_deterministe():
    """Deux fits identiques (même graine de données) → même historique."""
    hist1 = TorchFusionModel(engine_for_module(1)).fit(_samples_separables(), epochs=5)
    hist2 = TorchFusionModel(engine_for_module(1)).fit(_samples_separables(), epochs=5)
    assert hist1 == hist2, "l'entraînement doit être déterministe (zéro RNG)"


def test_fit_ensemble_vide_rejete():
    model = TorchFusionModel(engine_for_module(1))
    with pytest.raises(ValueError, match="aucun échantillon"):
        model.fit([])


# ── checkpoints ──────────────────────────────────────────────────────────────

def test_checkpoint_roundtrip(tmp_path):
    model = TorchFusionModel(engine_for_module(1))
    model.fit(_samples_separables(), epochs=5)
    ckpt = tmp_path / "fusion.pt"
    model.save(str(ckpt))
    clone = TorchFusionModel(engine_for_module(1))
    meta = clone.load_checkpoint(str(ckpt))
    assert meta["format"] == "medisuite-fusion-0.3"
    pl = _payload()
    assert clone.predict(pl) == model.predict(pl), \
        "les prédictions doivent être bit-à-bit identiques après reload"


# ── modalités manquantes (ADR-0018 conservé) ─────────────────────────────────

def test_modalite_manquante_inference_degradee():
    model = TorchFusionModel(engine_for_module(1))
    out = model.predict({"tabulaire": {"features": [55, 1, 9.8]}})
    assert out["modalites_manquantes"]["presentes"] == ["tabulaire"]
    assert "imaging_2d" in out["modalites_manquantes"]["absentes"]
    assert out["modalites_manquantes"]["complet"] is False
    assert out["detail"]["modalites_encodees"] == 1
    # importance renormalisée à 100 % sur la seule modalité présente
    assert sum(out["modality_importance_pct"].values()) == pytest.approx(100, abs=0.3)
    assert out["confiance"] < 0.7  # recalibrée à la baisse


def test_modalite_inconnue_rejete():
    model = TorchFusionModel(engine_for_module(1))
    with pytest.raises(ValueError, match="modalités inconnues"):
        model.predict({"ondes_cardiaques": {"signal": [1, 2, 3]}})


def test_aucune_modalite_rejete():
    model = TorchFusionModel(engine_for_module(1))
    with pytest.raises(ValueError, match="aucune modalité exploitable"):
        model.predict({})


# ── garde-fous (tâches non entraînables) ─────────────────────────────────────

def test_tache_survival_non_entrainable():
    engine = engine_for_module(4)  # config dont la tâche n'est pas entraînable
    engine.task = "survival"
    with pytest.raises(NotImplementedError, match="non entraînable"):
        TorchFusionModel(engine)


def test_incoherence_tache_tete_rejete():
    engine = engine_for_module(1)
    with pytest.raises(ValueError, match="incohérence"):
        TorchTaskHead("classification", MulticlassHead(32))


def test_trainable_tasks_constante():
    assert TRAINABLE_TASKS == {"classification", "multiclass", "regression"}
