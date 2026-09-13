"""Tests des datasets synthétiques : schéma, déterminisme, signal, ADR-0018.

Ces tests verrouillent les propriétés promises dans datasets/README.md :
1. le manifest couvre les 26 modules avec leurs SHA-256 ;
2. chaque ligne respecte le schéma de sa tâche (configs IA) ;
3. le générateur est DÉTERMINISTE (même seed → mêmes fichiers) ;
4. le signal est APPRENANT (discriminantes ∝ label) ;
5. la politique des modalités manquantes (ADR-0018) est respectée.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))  # datasets/ (registry.py)

import registry  # noqa: E402
from registry import MODULES, SPEC  # noqa: E402

MANIFEST = json.loads((ROOT / "datasets" / "manifest.json").read_text(encoding="utf-8"))


def _rows(slug: str, split: str) -> list[dict]:
    path = ROOT / "datasets" / slug / f"{split}.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]


# ---------------------------------------------------------------- 1. manifest

def test_manifest_couple_les_26_modules():
    slugs = {s for _, s in MODULES}
    assert set(MANIFEST["modules"]) == slugs
    for slug, entry in MANIFEST["modules"].items():
        assert entry["sha256_train"] and entry["sha256_val"], slug
        assert entry["n_train"] > 0 and entry["n_val"] > 0, slug
        assert entry["label_spec"] == SPEC[slug]["label"], slug


def test_manifest_sha256_cohérents_avec_fichiers():
    import hashlib
    for slug, entry in MANIFEST["modules"].items():
        for split in ("train", "val"):
            data = (ROOT / "datasets" / slug / f"{split}.jsonl").read_bytes()
            assert hashlib.sha256(data).hexdigest() == entry[f"sha256_{split}"], slug


# ---------------------------------------------------------------- 2. schéma

def test_schema_lignes_par_tache():
    for _, slug in MODULES:
        entry = MANIFEST["modules"][slug]
        task, attendues = entry["task"], set(entry["modalites"])
        lab = SPEC[slug]["label"]
        for split in ("train", "val"):
            rows = _rows(slug, split)
            assert len(rows) == entry[f"n_{split}"], slug
            for r in (rows[0], rows[-1]):
                assert r["slug"] == slug and r["task"] == task
                assert r["synthetique"] is True
                assert set(r["modalites"]) <= attendues, slug
                if task == "classification":
                    assert r["label"] in (0, 1)
                elif task == "multiclass":
                    assert 0 <= r["label"] < len(lab["classes"])
                elif task == "multilabel":
                    assert len(r["label"]) == len(lab["classes"])
                    assert set(r["label"]) <= {0, 1}
                else:  # regression / segmentation
                    assert lab["lo"] <= r["label"] <= lab["hi"]


# ---------------------------------------------------------------- 3. déterminisme

def test_determinisme_regeneration_cardiology(tmp_path):
    cmd = [sys.executable, str(ROOT / "datasets" / "generate.py"),
           "--outdir", str(tmp_path), "--only", "cardiology",
           "--seed", str(MANIFEST["seed"]),
           "--train", str(MANIFEST["modules"]["cardiology"]["n_train"]),
           "--val", str(MANIFEST["modules"]["cardiology"]["n_val"])]
    subprocess.run(cmd, check=True, capture_output=True)
    for split in ("train", "val"):
        regen = (tmp_path / "cardiology" / f"{split}.jsonl").read_bytes()
        orig = (ROOT / "datasets" / "cardiology" / f"{split}.jsonl").read_bytes()
        assert regen == orig  # bit-à-bit


# ---------------------------------------------------------------- 4. signal

def test_signal_apprenant_neurology():
    # neurology (binaire) : la moyenne des discriminantes doit séparer
    # label=1 de label=0 (sinon les smoke trains n'apprendraient rien)
    rows = _rows("neurology", "train")
    disc = SPEC["neurology"]["discriminantes"]
    for f in disc:
        m1 = [r["modalites"]["tabulaire"][f] for r in rows
              if r["label"] == 1 and "tabulaire" in r["modalites"]]
        m0 = [r["modalites"]["tabulaire"][f] for r in rows
              if r["label"] == 0 and "tabulaire" in r["modalites"]]
        assert m1 and m0 and abs(sum(m1) / len(m1) - sum(m0) / len(m0)) > 0, f


# ---------------------------------------------------------------- 5. ADR-0018

def test_modalites_manquantes_politique():
    for _, slug in MODULES:
        entry = MANIFEST["modules"][slug]
        primaire = entry["modalites"][0]
        for split in ("train", "val"):
            for r in _rows(slug, split):
                assert len(r["manquantes"]) <= 1, slug
                assert primaire in r["modalites"], slug  # jamais la primaire
                assert not (set(r["manquantes"]) & set(r["modalites"])), slug
