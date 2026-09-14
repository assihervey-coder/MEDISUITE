#!/usr/bin/env python3
"""CLI d'ingestion documentaire — documents bruts → unités de preuve (quarantaine).

Usage :
    # ingérer un document (→ corpus/quarantine/ en statut draft)
    python scripts/ingest_document.py data/raw/guidelines/who-malaria-guide-extrait.md

    # ingérer un dossier entier
    python scripts/ingest_document.py data/raw/ --recursive

    # promouvoir une unité validée par un humain (quarantaine → corpus actif)
    python scripts/ingest_document.py --promote corpus/quarantine/eu-draft-who-malaria-xxx-001.yaml \
        --authority WHO --edition-date 2023-06-01

    # lister la quarantaine
    python scripts/ingest_document.py --list-quarantine
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.config import CORPUS_DIR  # noqa: E402
from tropirag.evidence_engine.ingestion.pipeline import (  # noqa: E402
    DocumentIngestionPipeline,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingestion documentaire TropiRAG")
    ap.add_argument("paths", nargs="*", help="documents ou dossiers à ingérer")
    ap.add_argument("--recursive", action="store_true", help="parcours récursif")
    ap.add_argument("--promote", metavar="FILE",
                    help="promouvoir une unité draft (décision humaine)")
    ap.add_argument("--authority", help="autorité validée lors de la promotion")
    ap.add_argument("--edition-date", help="date d'édition validée (ISO)")
    ap.add_argument("--list-quarantine", action="store_true")
    ap.add_argument("--json", action="store_true", help="rapport en JSON")
    args = ap.parse_args()

    if args.list_quarantine:
        qdir = CORPUS_DIR / "quarantine"
        files = sorted(qdir.glob("*.yaml")) if qdir.exists() else []
        print(f"Quarantaine : {len(files)} unité(s) draft en attente de validation humaine")
        for f in files:
            print(f"  - {f.name}")
        return 0

    if args.promote:
        pipeline = DocumentIngestionPipeline()
        target = pipeline.promote(args.promote, authority=args.authority,
                                  edition_date=args.edition_date)
        print(f"Unité promue : {target}")
        return 0

    if not args.paths:
        ap.print_help()
        return 1

    pipeline = DocumentIngestionPipeline()
    reports = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            reports.extend(pipeline.ingest_directory(path) if args.recursive
                           else [pipeline.ingest(f) for f in sorted(path.iterdir())
                                 if f.is_file()])
        else:
            reports.append(pipeline.ingest(path))

    ok = [r for r in reports if r.status != "error"]
    total_units = sum(r.units_created for r in reports)
    if args.json:
        print(json.dumps([r.to_dict() for r in reports], ensure_ascii=False, indent=2))
    else:
        for r in reports:
            icon = {"draft": "+", "rejected": "×", "error": "!"}[r.status]
            print(f"[{icon}] {r.source_id or r.path} — {r.status}, "
                  f"{r.units_created} unité(s), {r.chunks_valid} chunks validés, "
                  f"{r.chunks_rejected} rejeté(s)")
            for w in r.warnings:
                print(f"      ⚠ {w}")
            for e in r.errors:
                print(f"      ✗ {e}")
        print(f"\nTotal : {len(ok)}/{len(reports)} document(s) ingéré(s), "
              f"{total_units} unité(s) draft en quarantaine")
    return 0 if total_units > 0 or not reports else 1


if __name__ == "__main__":
    raise SystemExit(main())
