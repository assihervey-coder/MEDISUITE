#!/usr/bin/env python3
"""Génère les datasets synthétiques des 26 modules MEDISUITE.

Pour chaque module (datasets/registry.py) :
  datasets/<slug>/train.jsonl  (n_train lignes)
  datasets/<slug>/val.jsonl    (n_val lignes)
+ datasets/manifest.json (schémas, comptages, SHA-256, seed).

Propriétés :
- DÉTERMINISTE avec flux RNG PAR MODULE (seed*100+no) : réexécuter avec le
  même seed reproduit les mêmes SHA-256, et régénérer un module seul
  (--only) donne les mêmes octets qu'une exécution complète.
- APPRENANT : les features discriminantes sont décalées en fonction du label
  (sinon les tests d'entraînement smoke ne pourraient rien apprendre).
- MODALITÉS MANQUANTES (ADR-0018) : ~8 % des lignes train / 15 % des lignes
  val perdent UNE modalité non primaire (dégradation élégante).
- AUCUNE DONNÉE RÉELLE : patients synthétiques (medisuite_core.seed).

Usage : python datasets/generate.py [--train 120] [--val 30] [--seed 42]
                                    [--outdir datasets] [--only slug]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in ("packages/medisuite-core",):
    sys.path.insert(0, str(ROOT / p))

import yaml  # noqa: E402  (PyYAML déjà requise par ai/multimodal/factory.py)

from medisuite_core import seed as ms_seed  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from registry import (MODULES, SPEC, GENOME_LEN,  # noqa: E402
                      VECTOR_DIM, VECTOR_MODALITIES, validate_spec)

CONFIG_DIR = ROOT / "ai" / "multimodal" / "configs"
REF_DATE = date(2026, 9, 14)
GEN_VERSION = "1.0.0"


def load_config_task(slug: str) -> tuple[str, list[str], int]:
    """Lit la config IA du module : (task, modalités attendues, d_model)."""
    matches = sorted(CONFIG_DIR.glob(f"*_{slug}.yaml"))
    if not matches:
        raise FileNotFoundError(f"config IA du module '{slug}' introuvable")
    with open(matches[0], encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    modalites = cfg.get("modalities", {}).get("attendues", ["tabulaire"])
    task = str(cfg.get("task", "classification"))
    # normalisation : les configs IA disent « binary », le schéma de dataset
    # (registry.SPEC) dit « classification » — même chose fonctionnellement.
    if task in ("binary", "classification"):
        task = "classification"
    return task, list(modalites), int(cfg.get("d_model", 32))


def draw_label(rng: random.Random, lab: dict) -> tuple:
    """Tire le label selon la tâche. Retourne (valeur, composant_apprenant)."""
    task = lab["task"]
    if task == "classification":
        y = 1 if rng.random() < lab["prevalence"] else 0
        return y, float(y)
    if task == "multiclass":
        y = rng.choices(range(len(lab["classes"])), weights=lab["poids"])[0]
        return y, y / (len(lab["classes"]) - 1)
    if task == "multilabel":
        ys = tuple(1 if rng.random() < p else 0 for p in lab["p"])
        comp = sum(ys) / max(1, len(ys))
        return ys, comp
    # regression / segmentation : cible bornée + composant normalisé
    v = rng.uniform(lab["lo"], lab["hi"])
    comp = (v - lab["lo"]) / (lab["hi"] - lab["lo"]) if lab["hi"] > lab["lo"] else 0.0
    return v, comp


def synth_modality(rng: random.Random, name: str, slug: str,
                   features: dict) -> object:
    """Payload synthétique d'une modalité, du type attendu par son encodeur."""
    if name in VECTOR_MODALITIES:
        return [round(rng.uniform(-1.0, 1.0), 3) for _ in range(VECTOR_DIM)]
    if name == "texte":
        return (f"{slug}: " +
                ", ".join(f"{k}={v:.2f}" for k, v in
                          list(features.items())[:2]) +
                ". Synthétique.")
    if name == "genomique":
        return "".join(rng.choices("ACGT", k=GENOME_LEN))
    raise ValueError(f"modalité inconnue : {name}")


def make_row(rng: random.Random, no: int, slug: str, task: str,
             modalites: list[str], offset: int, split: str) -> dict:
    spec = SPEC[slug]
    patient = ms_seed.generate_patient(rng, 1)[0]
    age = ms_seed.age_from(patient["date_naissance"], REF_DATE)
    label, comp = draw_label(rng, spec["label"])

    features: dict[str, float] = {}
    for i, (name, (lo, hi)) in enumerate(spec["features"].items()):
        v = rng.uniform(lo, hi)
        # signal apprenant : décalage de 25 % de l'amplitude sur les
        # discriminantes, proportionnel au composant du label
        if name in spec["discriminantes"]:
            amp = (hi - lo) * 0.25
            v = min(hi, max(lo, lo + (v - lo) + amp * (comp - 0.5) * 2
                            * (1 if i % 2 == 0 else -1)))
        features[name] = round(v, 3)

    manquantes: list[str] = []
    if modalites and rng.random() < (0.08 if split == "train" else 0.15):
        # jamais la modalité primaire (index 0) — ADR-0018, dégradation
        candidats = modalites[1:]
        if candidats:
            manquantes = [rng.choice(candidats)]

    modalites_out: dict[str, object] = {}
    for m in modalites:
        if m in manquantes:
            continue
        if m == "tabulaire":
            modalites_out[m] = dict(features)
        else:
            modalites_out[m] = synth_modality(rng, m, slug, features)

    return {
        "id": f"m{no:02d}-{split[0]}{offset:05d}",
        "module": no, "slug": slug, "split": split, "task": task,
        "patient": {"id": patient["id"], "sexe": patient["sexe"], "age": age},
        "modalites": modalites_out, "manquantes": manquantes,
        "label": label,
        "synthetique": True,
    }


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train", type=int, default=120)
    ap.add_argument("--val", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--outdir", default=str(ROOT / "datasets"))
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    validate_spec()
    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    manifest = {
        "generateur": "datasets/generate.py", "version_generateur": GEN_VERSION,
        "seed": args.seed, "date_generation": REF_DATE.isoformat(),
        "note": "Synthétique — AUCUNE donnée réelle. Signaux artificiels "
                "destinés aux tests d'intégration de la fusion, aux smoke "
                "trains et aux démonstrations de drift. Interdit pour "
                "l'entraînement clinique validé (voir dossier CE, R5-R6).",
        "modules": {},
    }

    for no, slug in MODULES:
        if args.only and slug != args.only:
            continue
        task, modalites, d_model = load_config_task(slug)
        spec = SPEC[slug]
        rng = random.Random(args.seed * 100 + no)  # flux par module
        mdir = outdir / slug
        mdir.mkdir(exist_ok=True)
        entry = {"no": no, "task": task, "modalites": modalites,
                 "d_model": d_model, "features": sorted(spec["features"]),
                 "discriminantes": spec["discriminantes"],
                 "label_spec": spec["label"]}
        for split, n in (("train", args.train), ("val", args.val)):
            path = mdir / f"{split}.jsonl"
            with open(path, "w", encoding="utf-8") as fh:
                for i in range(n):
                    row = make_row(rng, no, slug, task, modalites, i + 1, split)
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            entry[f"n_{split}"] = n
            entry[f"sha256_{split}"] = sha256_file(path)
        manifest["modules"][slug] = entry
        print(f"  ✅ {slug:<18} train={args.train} val={args.val} task={task}")

    with open(outdir / "manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"\nmanifest.json : {len(manifest['modules'])} modules — "
          f"datasets/ (seed {args.seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
