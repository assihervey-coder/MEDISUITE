#!/usr/bin/env python3
"""Génère des patients synthétiques (aucune donnée réelle) au format JSON."""
import json
import random
import sys

sys.path.insert(0, "packages/medisuite-core")
from medisuite_core.seed import generate_patient  # noqa: E402

rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 2026)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
print(json.dumps(generate_patient(rng, n), ensure_ascii=False, indent=2))
