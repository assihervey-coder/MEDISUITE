#!/usr/bin/env python3
"""Affiche l'arborescence du monorepo (version légère de tree)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", "node_modules", "__pycache__", ".pytest_cache", "dist", "data"}


def walk(d: Path, prefix: str = "") -> None:
    entries = sorted(p for p in d.iterdir() if p.name not in SKIP)
    dirs = [e for e in entries if e.is_dir()]
    files = [e for e in entries if e.is_file()]
    for e in dirs:
        print(f"{prefix}├── {e.name}/")
        walk(e, prefix + "│   ")
    for e in files[:6]:
        print(f"{prefix}├── {e.name}")
    if len(files) > 6:
        print(f"{prefix}├── … (+{len(files) - 6} fichiers)")


print("MEDISUITE/")
walk(ROOT)
