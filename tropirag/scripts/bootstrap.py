#!/usr/bin/env python3
"""TropiRAG — bootstrap (voir make help)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
# bootstrap : charge règles + corpus + registre

from tropirag.clinical_engine.rules.rule_loader import load_rule_engine
from tropirag.evidence_engine.evidence_engine import EvidenceEngine
from tropirag.ai.registry.model_registry import get_registry

eng = load_rule_engine()
ee = EvidenceEngine()
units = ee.load()
reg = get_registry()
print(f"Bootstrap OK : {eng.count()} règles, {units} unités de preuve, "
      f"{len(reg.all())} modèles déclarés.")
