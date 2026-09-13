"""Adaptateur FHIR — V1 : lecture des profils IOP committés (ADR-0024)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROFILES = ROOT / "services" / "integration-service" / "fhir" / "profiles"


def list_profiles() -> list[str]:
    return sorted(p.name for p in PROFILES.glob("*.json"))


def profile_snapshot() -> dict[str, str]:
    """{fichier: sha256} — entrée du compatibility-engine pour FHIR."""
    import hashlib
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in PROFILES.glob("*.json")}


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))
