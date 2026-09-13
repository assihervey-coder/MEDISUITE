"""Contexte applicatif — dépôts et chemins partagés des cas d'usage."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


@dataclass(slots=True)
class AppContext:
    """Filaire des dépôts filesystem (V1) — remplaçable par Postgres en V2."""

    root: Path = ROOT

    @property
    def proposals_store(self) -> Path:
        return self.root / "governance" / "proposals" / "registry" / "proposals-runtime.json"

    @property
    def assessments_dir(self) -> Path:
        return self.root / "evidence" / "evolution"

    @property
    def changesets_dir(self) -> Path:
        return self.root / "releases" / "manifests"

    @property
    def decisions_dir(self) -> Path:
        return self.root / "audit" / "approvals"

    @property
    def audit_file(self) -> Path:
        return self.root / "audit" / "evolution" / "events.jsonl"


def _repo(module_path: str):
    """Charge un dépôt du domaine via l'alias ecp (import paresseux sûr)."""
    import importlib
    return importlib.import_module(module_path)
