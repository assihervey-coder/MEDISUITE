"""Manifeste de preuves — empreinte du corpus pour l'audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def build_manifest(corpus_dir: Path) -> dict:
    units_dir = corpus_dir / "evidence_units"
    files = sorted(units_dir.glob("*.yaml"))
    manifest = {
        "units": [],
        "corpus_sha256": hashlib.sha256(
            "".join(f.read_text(encoding="utf-8") for f in files).encode("utf-8")
        ).hexdigest()[:16],
    }
    for f in files:
        manifest["units"].append({
            "file": f.name,
            "sha256": hashlib.sha256(f.read_bytes()).hexdigest()[:12],
        })
    return manifest


def write_manifest(corpus_dir: Path) -> Path:
    m = build_manifest(corpus_dir)
    out = corpus_dir / "manifests" / "integrity_manifest.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    return out
