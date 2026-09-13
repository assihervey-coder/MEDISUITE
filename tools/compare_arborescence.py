#!/usr/bin/env python3
"""Couverture de l'arborescence initiale MEDISUITE vs dépôt réel. v0.8.

Reproduit l'audit de docs/COUVERTURE-ARBRE-INITIAL.md :
  python tools/compare_arborescence.py <arborescence.txt> [--repo /chemin] [--json out.json]

Lecture du fichier d'arborescence (entrées ├──/└──, emoji 📂, expansion
{a,b,c}) → chemins relatifs aspirés ; parcours du dépôt → chemins réels ;
correspondance EXACT puis FAMILLE (répertoire parent identique + nom de base
normalisé) ; liste inverse des fichiers réels hors plan.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from collections import defaultdict


def expand_braces(name: str) -> list[str]:
    if name.startswith("{") and name.endswith("}"):
        name = name[1:-1]
    if "," in name and "." in name:
        return [p.strip() for p in name.split(",") if p.strip()]
    return [name]


def parse_tree(txt_path: str):
    files, dirs = set(), set()
    stack: list[str] = []
    with open(txt_path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            m = re.search(r"[├└]──\s*(\S.*)$", line)
            if not m:
                continue
            name = m.group(1).strip()
            if name.startswith("📂 "):
                name = name[2:].strip()
            name = name.split("#")[0].strip()
            if not name or name in ("text", "…"):
                continue
            prefix = line[: m.start()]
            depth = prefix.count("│   ") + prefix.count("    ")
            stack = stack[:depth]
            base = name.rstrip("/")
            if name.endswith("/"):
                dirs.add("/".join(stack + [base]))
                stack.append(base)
                continue
            for part in expand_braces(base):
                fpath = "/".join(stack + [part])
                (dirs if part.endswith("/") else files).add(fpath)
    return files, dirs


def walk_repo(repo: str) -> set[str]:
    out = set()
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "node_modules", "__pycache__",
                                    ".venv", "dist")]
        for f in filenames:
            out.add(os.path.relpath(os.path.join(dirpath, f),
                                    repo).replace(os.sep, "/"))
    return out


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", name.lower())
    return re.sub(r"[^a-z0-9]+", "", s)


def top2(path: str) -> str:
    parts = path.split("/")
    return "/".join(parts[:2]) if len(parts) > 1 else parts[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tree", help="fichier texte de l'arborescence initiale")
    ap.add_argument("--repo", default=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    aspir_files, aspir_dirs = parse_tree(args.tree)
    real = walk_repo(args.repo)

    real_by_top2 = defaultdict(list)
    for p in real:
        real_by_top2[top2(p)].append(p)

    exact, family, missing = [], [], []
    for p in sorted(aspir_files):
        if p in real:
            exact.append(p)
            continue
        base = os.path.basename(p)
        nb = norm(base)
        cand = real if "/" not in p else real_by_top2.get(top2(p), [])
        hit = next((r for r in cand
                    if norm(os.path.basename(r)) in (nb, nb + "yml")
                    or norm(os.path.basename(r)) + "yml" == nb), None)
        (family.append((p, hit)) if hit else missing.append(p))

    reverse = sorted(p for p in real if p not in aspir_files)
    by_top = defaultdict(int)
    for p in aspir_files:
        by_top[p.split("/")[0]] += 1

    stats = {
        "aspirationnels_fichiers": len(aspir_files),
        "aspirationnels_repertoires": len(aspir_dirs),
        "reels_fichiers": len(real),
        "exact": len(exact),
        "famille": len(family),
        "manquants": len(missing),
        "hors_plan_reverse": len(reverse),
        "par_top_aspirationnel": dict(sorted(by_top.items(),
                                             key=lambda kv: -kv[1])),
    }
    print(json.dumps(stats, ensure_ascii=False, indent=1))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"stats": stats, "exact": exact, "famille": family,
                       "manquants": missing, "reverse": reverse},
                      fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
