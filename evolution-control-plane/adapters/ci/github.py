"""Adaptateur CI — V1 : lecture du workflow local (ci.yml) comme contrat."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CI_FILE = ROOT / ".github" / "workflows" / "ci.yml"


def required_jobs_before_docker_publish() -> list[str]:
    """Les jobs dont docker-publish dépend (publication seulement si vert)."""
    if not CI_FILE.exists():
        return []
    text = CI_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "needs:" in line and "packages-integration" in line:
            inner = line.split("needs:", 1)[1].strip().strip("[]")
            return [j.strip() for j in inner.split(",") if j.strip()]
    return []
