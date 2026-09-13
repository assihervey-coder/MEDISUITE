#!/usr/bin/env python3
"""Générateur SBOM MEDISUITE — CycloneDX 1.5 JSON (stdlib, jalon R4).

Inventorie les dépendances Python du dépôt (requirements.txt racine + par
service) et, si exécuté dans l'environnement actif, les versions réellement
installées (importlib.metadata — zéro dépendance).

Usage :
    python3 tools/sbom/generate_sbom.py -o sbom.json
    python3 tools/sbom/generate_sbom.py --summary
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as im
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_REQ_LINE = re.compile(r"^\s*([A-Za-z0-9._-]+)([<>=!~]+[^\s#;]+)?\s*(#.*)?$")


def _parse(path: Path, component: str) -> list[tuple[str, str]]:
    rows = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            m = _REQ_LINE.match(line)
            if m:
                rows.append((component, line))
    except OSError:
        pass
    return rows


def discover_requirements() -> list[tuple[str, str]]:
    """(composant, exigence) pour chaque requirement du monorepo."""
    out: list[tuple[str, str]] = []
    for path in sorted(ROOT.glob("requirements*.txt")):
        out += _parse(path, component="monorepo")
    for path in sorted(ROOT.glob("services/*/requirements.txt")):
        out += _parse(path, component=f"services/{path.parent.name}")
    for path in sorted(ROOT.glob("packages/*/requirements.txt")):
        out += _parse(path, component=f"packages/{path.parent.name}")
    return out


def installed_version(name: str) -> str | None:
    try:
        return im.version(name)
    except im.PackageNotFoundError:
        return None


def build_sbom() -> dict:
    components: dict[str, dict] = {}
    for component, requirement in discover_requirements():
        m = _REQ_LINE.match(requirement)
        name = m.group(1) if m else requirement
        pinned = (m.group(2) or "").lstrip("=<>!~") if m else ""
        key = name.lower()
        if key not in components:
            ver = installed_version(name)
            components[key] = {
                "type": "library", "bom-ref": f"pypi:{key}", "name": key,
                "version": ver or pinned or "UNRESOLVED",
                "purl": f"pkg:pypi/{key}" + (f"@{ver}" if ver else ""),
                "scope": "required",
                "properties": [
                    {"name": "medisuite:required-as", "value": requirement},
                    {"name": "medisuite:used-by", "value": component},
                ],
            }
        else:
            components[key]["properties"].append(
                {"name": "medisuite:used-by", "value": component})

    app = {
        "type": "application", "bom-ref": "medisuite", "name": "medisuite",
        "version": _app_version(), "purl": "pkg:generic/medisuite",
    }
    return {
        "bomFormat": "CycloneDX", "specVersion": "1.5", "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": app,
            "properties": [
                {"name": "medisuite:purpose",
                 "value": "SBOM réglementaire (MDR/EGSP §15, ASVS 14) — jalon R4"},
                {"name": "medisuite:generator",
                 "value": "tools/sbom/generate_sbom.py (stdlib)"},
            ],
        },
        "components": sorted(components.values(), key=lambda c: c["name"]),
    }


def _app_version() -> str:
    try:
        head = (ROOT / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = (ROOT / ".git" / head[5:]).read_text().strip()
            return f"git-{ref[:12]}"
        return head[:12]
    except OSError:
        return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-o", "--output", default="sbom.json")
    ap.add_argument("--summary", action="store_true",
                    help="affiche un résumé au lieu d'écrire le JSON")
    args = ap.parse_args()

    sbom = build_sbom()
    comps = sbom["components"]
    unresolved = [c for c in comps if c["version"] == "UNRESOLVED"]
    if args.summary:
        print(f"Composants : {len(comps)}")
        print(f"  résolus (installés ou épinglés) : {len(comps) - len(unresolved)}")
        print(f"  UNRESOLVED                      : {len(unresolved)}")
        used_by = sum(1 for c in comps
                      for p in c.get("properties", []) if p["name"] == "medisuite:used-by")
        print(f"  références composant→service    : {used_by}")
        if unresolved:
            print("Attention (à épingler) :",
                  ", ".join(c["name"] for c in unresolved[:10]))
        return 0
    data = json.dumps(sbom, indent=2, ensure_ascii=False).encode()
    Path(args.output).write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"SBOM : {os.path.abspath(args.output)} ({len(comps)} composants, "
          f"sha256 {digest[:16]}…)")
    if unresolved:
        print(f"⚠ {len(unresolved)} composants non résolus — voir --summary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
