"""Cas d'usage — régression ciblée/complete (exécution pytest réelle)."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def run_regression(suites: list[str], timeout: int = 900) -> dict:
    """Exécute pytest sur les suites données ; retourne le verdict."""
    existing = [s for s in suites if (ROOT / s).exists()]
    if not existing:
        return {"verdict": "NOT_RUN", "passed": 0, "failed": 0, "suites": suites}
    proc = subprocess.run(
        ["python", "-m", "pytest", *existing, "-q", "--no-header"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    passed = failed = 0
    for token in proc.stdout.replace(",", " ").split():
        if token.endswith("passed"):
            passed = int(token.split("passed")[0] or 0)
        if token.endswith("failed"):
            failed = int(token.split("failed")[0] or 0)
    return {"verdict": "PASS" if proc.returncode == 0 else "FAIL",
            "passed": passed, "failed": failed, "suites": existing,
            "tail": proc.stdout[-300:]}
