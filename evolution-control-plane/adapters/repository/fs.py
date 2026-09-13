"""Adaptateur dépôt filesystem — JSON (V1)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FsStore:
    """Petit store JSON générique (un fichier par clé)."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def write(self, key: str, payload: dict[str, Any]) -> Path:
        p = self._root / f"{key}.json"
        p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return p

    def read(self, key: str) -> dict[str, Any] | None:
        p = self._root / f"{key}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


class GitAdapter:
    """Adaptateur git local — version courante + commit de baseline."""

    def __init__(self, repo_root: Path) -> None:
        self._root = Path(repo_root)

    def current_version(self) -> str:
        import re
        try:
            changelog = (self._root / "CHANGELOG.md").read_text(encoding="utf-8")
            m = re.search(r"## \[?(v?\d+\.\d+\.\d+)", changelog)
            return m.group(1).lstrip("v") if m else "0.0.0"
        except OSError:
            return "0.0.0"

    def current_commit(self) -> str:
        import subprocess
        try:
            return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                  cwd=str(self._root), capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return "unknown"
