"""Cas d'usage — exécution d'une unit de changement (V1 : déclaratif vérifié)."""
from __future__ import annotations

import subprocess
from pathlib import Path


def execute_change(unit: dict, root: Path) -> dict:
    """V1 : l'exécution reste humaine outillée ; le control plane VÉRIFIE.

    Si `verify` est une commande (pytest…), elle est jouée en sous-processus.
    """
    verify = unit.get("verify", "")
    if not verify:
        return {"unit": unit.get("component"), "executed": False,
                "verified": False, "detail": "aucune commande de vérification déclarée"}
    proc = subprocess.run(verify, shell=True, cwd=str(root), capture_output=True,
                          text=True, timeout=600)
    return {"unit": unit.get("component"), "executed": True,
            "verified": proc.returncode == 0,
            "detail": (proc.stdout or proc.stderr)[-400:]}
