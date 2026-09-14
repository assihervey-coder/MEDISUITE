#!/usr/bin/env python3
"""Benchmark des modèles du mesh (latence, disponibilité) — nécessite les nœuds."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.ai.gateways.ollama_gateway import OllamaGateway  # noqa: E402
from tropirag.ai.registry.model_registry import get_registry  # noqa: E402


def main() -> int:
    reg = get_registry()
    gw = OllamaGateway()
    print(f"{'modèle':30s} {'dispo':8s}")
    for m in reg.all():
        t0 = time.perf_counter()
        up = gw.is_available(m.model_id)
        ms = (time.perf_counter() - t0) * 1000
        print(f"{m.model_id:30s} {'OUI' if up else 'non':8s} ({ms:.0f} ms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
