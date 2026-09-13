"""Test Impact Engine — carte composants → suites de tests réelles du repo."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# Carte de dépendance test (dérivée de la baseline — mise à jour avec elle)
SUITE_MAP: dict[str, list[str]] = {
    "medisuite-core": ["packages/medisuite-core/tests/"],
    "clinical-rules": ["packages/clinical-rules/tests/"],
    "datasets": ["datasets/tests/"],
    "integration-service": ["services/integration-service/tests/"],
    "evolution-control-plane": ["evolution-control-plane/tests/"],
    "infrastructure": ["tools/tests/"],
    "compliance": ["tools/tests/"],
    "web-portal": ["apps/web-portal (vitest + e2e Playwright)"],
    "security": ["tools/tests/"],
}
SPECIALTY_PATTERN = "services/{slug}/tests/"


def _suite_for_component(component: str) -> list[str]:
    if component in SUITE_MAP:
        return SUITE_MAP[component]
    if component.endswith("-service") or component == "api-gateway":
        suite = SPECIALTY_PATTERN.format(slug=component)
        return [suite]
    if component == "ai-multimodal":
        return ["ai/multimodal/tests/"]
    return []


def dependency_mapper(changed_paths: list[str]) -> dict[str, list[str]]:
    """{composant: [suites]} — composants réellement touchés."""
    mapping: dict[str, list[str]] = {}
    for path in changed_paths:
        comp = _component(path)
        suites = [s for s in _suite_for_component(comp)
                  if (ROOT / s).exists() or s.startswith("apps/")]
        if suites:
            mapping.setdefault(comp, [])
            for s in suites:
                if s not in mapping[comp]:
                    mapping[comp].append(s)
    return mapping


def _component(path: str) -> str:
    p = path.strip("/")
    if p.startswith("services/"):
        return p.split("/")[1]
    if p.startswith("packages/medisuite-core"):
        return "medisuite-core"
    if p.startswith("packages/clinical-rules"):
        return "clinical-rules"
    if p.startswith("ai/"):
        return "ai-multimodal"
    if p.startswith("datasets/"):
        return "datasets"
    if p.startswith("apps/web-portal"):
        return "web-portal"
    if p.startswith(("infrastructure/", "monitoring/", "security/", "compliance/",
                     "tools/", "governance/", "contracts/", "architecture/",
                     "evolution-control-plane/", "feature-flags/", "migrations/",
                     "evidence/", "releases/", "audit/", "validation/",
                     "compatibility/")):
        return "infrastructure"
    return "repo-root"
