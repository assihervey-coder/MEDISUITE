"""Chargement du référentiel complet de règles TropiRAG."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from tropirag.core.config import RULES_DIR
from tropirag.core.errors import RuleLoadError
from tropirag.clinical_engine.rules.rule_engine import RuleEngine


@lru_cache(maxsize=1)
def load_rule_engine() -> RuleEngine:
    """Charge toutes les règles de rules/ (singleton process)."""
    engine = RuleEngine()
    if not RULES_DIR.exists():
        raise RuleLoadError(f"Répertoire de règles introuvable: {RULES_DIR}")
    n = engine.load_directory(RULES_DIR)
    if n == 0:
        raise RuleLoadError("Aucune règle chargée — référentiel vide")
    return engine
