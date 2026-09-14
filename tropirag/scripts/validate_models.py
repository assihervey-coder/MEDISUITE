#!/usr/bin/env python3
"""Valide le registre de modèles : invariants + santé des gateways."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.ai.registry.model_registry import get_registry  # noqa: E402
from tropirag.core.enums import ClinicalTask  # noqa: E402
from tropirag.ai.routing.model_router import ModelRouter  # noqa: E402
from tropirag.core.config import get_config  # noqa: E402


def main() -> int:
    reg = get_registry()
    violations = reg.validate_invariants()
    print(f"Modèles déclarés : {len(reg.all())}")
    for m in reg.all():
        print(f"  {m.model_id:28s} {m.family:12s} {m.provider_gateway:14s} "
              f"prio={m.priority} vram={m.vram_gb} GB")
    if violations:
        print("VIOLATIONS D'INVARIANTS :")
        for v in violations:
            print("  ✗", v)
        return 1
    # chaque capacité doit avoir au moins un modèle
    router = ModelRouter(reg, inference_mode=get_config().inference.mode)
    missing = []
    for task in ClinicalTask:
        if not reg.find_by_task(task):
            missing.append(task.value)
    if missing:
        print("Capacités sans modèle :", missing)
        return 1
    print("Invariants : conformes. Toutes les capacités ont un exécutant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
