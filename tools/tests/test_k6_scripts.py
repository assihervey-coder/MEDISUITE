"""Verrou syntaxique des scénarios k6 (v0.12).

k6 n'est pas installé dans la CI standard (binaire Go) : ce test garantit
que chaque script de charge est du JavaScript/ESM VALIDE (parsing node,
aucune résolution de module — les imports `k6/*` sont fournis au runtime
par k6). Un script qui ne parse pas ne doit jamais atteindre le runner.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

LOAD = Path(__file__).resolve().parents[2] / "testing" / "load"
SCRIPTS = ["k6-smoke.js", "k6-stress.js"]


@pytest.mark.parametrize("name", SCRIPTS)
def test_k6_script_parses(name: str) -> None:
    node = shutil.which("node")
    if node is None:  # pragma: no cover — CI fournit node 20
        pytest.skip("node indisponible")
    script = (LOAD / name).read_text(encoding="utf-8")
    proc = subprocess.run(
        [node, "--input-type=module", "--check"],
        input=script, capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"{name} : syntaxe invalide\n{proc.stderr}"


def test_k6_thresholds_egsp_present() -> None:
    """Le seuil EGSP p95 ≤ 2000 ms doit être explicite dans chaque script."""
    for name in SCRIPTS:
        text = (LOAD / name).read_text(encoding="utf-8")
        assert "2000" in text, f"{name} : seuil EGSP p95 absente"
        assert "thresholds" in text, f"{name} : bloc thresholds absent"
