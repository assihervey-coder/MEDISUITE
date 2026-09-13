"""Dépôt de change sets — JSON par change set (releases/manifests adjacents)."""
from __future__ import annotations

import json
from pathlib import Path

from .change_set import ChangeSet
from ..proposal.value_objects import ChangeSetId


class ChangeSetRepository:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, change_set: ChangeSet) -> Path:
        p = self._root / f"{change_set.id.value}.changeset.json"
        p.write_text(json.dumps(change_set.to_dict(), indent=2, ensure_ascii=False),
                     encoding="utf-8")
        return p

    def get(self, change_set_id: str) -> dict | None:
        p = self._root / f"{change_set_id}.changeset.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def next_id(self) -> ChangeSetId:
        existing = [int(p.stem.split("-")[1]) for p in
                    self._root.glob("CHG-*.changeset.json")]
        return ChangeSetId(f"CHG-{max(existing, default=0) + 1:04d}")
