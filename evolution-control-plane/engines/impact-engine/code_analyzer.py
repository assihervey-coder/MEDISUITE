"""Analyseur code — nombre de fichiers/services touchés via la baseline."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _component_of(path: str) -> str:
    """Mappe un chemin repo → composant baseline (approximation déterministe)."""
    p = path.strip("/")
    if p.startswith("services/"):
        return p.split("/")[1]
    if p.startswith("packages/medisuite-core"):
        return "medisuite-core"
    if p.startswith("packages/clinical-rules"):
        return "clinical-rules"
    if p.startswith("ai/"):
        return "ai-multimodal"
    if p.startswith("apps/web-portal"):
        return "web-portal"
    if p.startswith("datasets/"):
        return "datasets"
    if p.startswith(("infrastructure/", "monitoring/")):
        return "infrastructure"
    if p.startswith("security/"):
        return "security"
    if p.startswith("compliance/"):
        return "compliance"
    if p.startswith(("governance/", "contracts/", "architecture/",
                     "evolution-control-plane/")):
        return "evolution-control-plane"
    return "repo-root"


def analyze_files(changed_paths: list[str]) -> dict:
    """Retourne {files, services, components:{...}} depuis les chemins réels."""
    components: dict[str, int] = {}
    for path in changed_paths:
        comp = _component_of(path)
        components[comp] = components.get(comp, 0) + 1
    services = sum(1 for c in components
                   if c.endswith("-service") or c == "api-gateway")
    # fichiers réellement présents (vérification de réalité)
    existing = sum(1 for p in changed_paths if (ROOT / p).exists())
    return {
        "files": len(changed_paths),
        "files_existing": existing,
        "services": services,
        "components": components,
    }
