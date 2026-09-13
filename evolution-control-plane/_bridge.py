"""Pont d'importation du control plane.

Les répertoires canoniques contiennent des tirets (`evolution-control-plane`,
`impact-engine`) — invalides dans la syntaxe `import`. Ce module enregistre
l'alias **`ecp`** dans `sys.modules` (plus les alias underscore des moteurs)
pour rendre tout l'arbre importable normalement :

    from ecp.domain.proposal.enums import ProposalState
    from ecp.engines.impact_engine.engine import ImpactEngine

Point d'entrée unique : `register()`. Idempotent.
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
ALIAS = "ecp"
ENGINE_ALIASES = {
    "impact_engine": "impact-engine",
    "risk_engine": "risk-engine",
    "compatibility_engine": "compatibility-engine",
    "test_impact_engine": "test-impact-engine",
    "rollout_engine": "rollout-engine",
}


def register():
    """Enregistre l'alias `ecp` (+ moteurs underscore) et retourne le package."""
    if ALIAS in sys.modules:
        return sys.modules[ALIAS]
    spec = importlib.util.spec_from_file_location(
        ALIAS, PKG_DIR / "__init__.py", submodule_search_locations=[str(PKG_DIR)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[ALIAS] = pkg
    spec.loader.exec_module(pkg)

    engines_dir = PKG_DIR / "engines"
    if engines_dir.exists():
        engines_pkg = importlib.import_module(f"{ALIAS}.engines")
        for alias, real in ENGINE_ALIASES.items():
            real_dir = engines_dir / real
            if real_dir.exists() and (real_dir / "__init__.py").exists():
                sp = importlib.util.spec_from_file_location(
                    f"{ALIAS}.engines.{alias}", real_dir / "__init__.py",
                    submodule_search_locations=[str(real_dir)])
                mod = importlib.util.module_from_spec(sp)
                sys.modules[f"{ALIAS}.engines.{alias}"] = mod
                sp.loader.exec_module(mod)
                setattr(engines_pkg, alias, mod)
    return pkg
