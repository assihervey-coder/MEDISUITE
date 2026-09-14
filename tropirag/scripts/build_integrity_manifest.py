#!/usr/bin/env python3
"""Génère et vérifie les manifests du corpus — intégrité et versioning.

Manifests produits (corpus/manifests/) :
    - source_manifest.yaml   : inventaire des sources déclarées
    - version_manifest.yaml  : historique des versions du corpus
    - integrity_manifest.yaml: SHA-256 de chaque unité + totaux

Modes :
    python scripts/build_integrity_manifest.py            # génère
    python scripts/build_integrity_manifest.py --verify    # vérifie (exit 1 si écart)
    python scripts/build_integrity_manifest.py --strict    # vérifie + quarantaine saine
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.config import CORPUS_DIR  # noqa: E402

MANIFESTS = CORPUS_DIR / "manifests"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def generate() -> int:
    units_dir = CORPUS_DIR / "evidence_units"
    units = sorted(p for p in units_dir.glob("*.yaml")
                  if p.name != "corpus_manifest.yaml")
    sources = sorted((CORPUS_DIR / "sources").rglob("*.yaml"))
    quarantine = sorted((CORPUS_DIR / "quarantine").glob("*.yaml")) \
        if (CORPUS_DIR / "quarantine").exists() else []

    # --- source_manifest ---------------------------------------------------
    source_rows = []
    for s in sources:
        with open(s, encoding="utf-8") as fh:
            meta = yaml.safe_load(fh) or {}
        source_rows.append({
            "source_id": meta.get("source_id") or s.stem,
            "authority": meta.get("authority", "unknown"),
            "title": meta.get("title", ""),
            "jurisdiction": meta.get("jurisdiction", "INT"),
            "edition_date": meta.get("edition_date"),
            "file": str(s.relative_to(CORPUS_DIR)),
            "sha256": _sha256(s),
        })

    # --- version_manifest : historique cumulatif ----------------------------
    version_path = MANIFESTS / "version_manifest.yaml"
    history: list[dict] = []
    if version_path.exists():
        with open(version_path, encoding="utf-8") as fh:
            history = (yaml.safe_load(fh) or {}).get("versions", [])

    # --- integrity_manifest ------------------------------------------------
    unit_rows = []
    for u in units:
        unit_rows.append({"unit_id": u.stem, "sha256": _sha256(u),
                          "bytes": u.stat().st_size})
    corpus_hash = hashlib.sha256(
        "".join(r["sha256"] for r in unit_rows).encode()).hexdigest()
    today = time.strftime("%Y-%m-%d")

    current = {
        "version": f"auto-{today}",
        "date": today,
        "units": len(unit_rows),
        "sources": len(source_rows),
        "corpus_sha256": corpus_hash,
    }
    if not history or history[-1].get("corpus_sha256") != current["corpus_sha256"]:
        history.append(current)

    MANIFESTS.mkdir(parents=True, exist_ok=True)

    def _dump(path: Path, payload: dict) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)

    _dump(MANIFESTS / "source_manifest.yaml", {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sources_total": len(source_rows),
        "sources": source_rows,
    })
    _dump(MANIFESTS / "integrity_manifest.yaml", {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "units_total": len(unit_rows),
        "corpus_sha256": corpus_hash,
        "units": unit_rows,
    })
    _dump(version_path, {
        "current": current,
        "versions": history,
    })

    print(f"Manifests générés : {len(source_rows)} sources, {len(unit_rows)} unités, "
          f"corpus_sha256={corpus_hash[:16]}…")
    print(f"Quarantaine : {len(quarantine)} unité(s) draft (hors corpus actif)")
    return 0


def verify(strict: bool = False) -> int:
    integrity_path = MANIFESTS / "integrity_manifest.yaml"
    if not integrity_path.exists():
        print("✗ integrity_manifest.yaml absent — lancez la génération d'abord")
        return 1
    with open(integrity_path, encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh) or {}
    problems: list[str] = []
    for row in manifest.get("units", []):
        p = CORPUS_DIR / "evidence_units" / f"{row['unit_id']}.yaml"
        if not p.exists():
            problems.append(f"{row['unit_id']}: fichier disparu")
            continue
        if _sha256(p) != row["sha256"]:
            problems.append(f"{row['unit_id']}: SHA-256 divergent — fichier modifié")
    # unités non-référencées
    known = {r["unit_id"] for r in manifest.get("units", [])}
    for p in (CORPUS_DIR / "evidence_units").glob("*.yaml"):
        if p.stem not in known and p.name != "corpus_manifest.yaml":
            problems.append(f"{p.stem}: présente dans le corpus, absente du manifest")
    if strict:
        quarantine = list((CORPUS_DIR / "quarantine").glob("*.yaml")) \
            if (CORPUS_DIR / "quarantine").exists() else []
        for q in quarantine:
            with open(q, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            if data.get("status") != "draft":
                problems.append(f"{q.stem}: statut quarantaine incohérent")
    if problems:
        for p in problems:
            print(f"✗ {p}")
        print(f"INTÉGRITÉ : {len(problems)} problème(s)")
        return 1
    print(f"✓ Intégrité vérifiée : {len(known)} unités conformes "
          f"(corpus_sha256={manifest.get('corpus_sha256', '')[:16]}…)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Manifests d'intégrité du corpus")
    ap.add_argument("--verify", action="store_true", help="vérifier au lieu de générer")
    ap.add_argument("--strict", action="store_true",
                    help="vérification étendue (quarantaine saine)")
    args = ap.parse_args()
    if args.verify or args.strict:
        return verify(strict=args.strict)
    return generate()


if __name__ == "__main__":
    raise SystemExit(main())
