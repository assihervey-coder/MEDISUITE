"""Dépôt de décisions — JSONL append-only (audit/approvals/)."""
from __future__ import annotations

import json
from pathlib import Path

from .entities import Decision


class DecisionRepository:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._file = self._root / "decisions.jsonl"

    def append(self, decision: Decision) -> None:
        with self._file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(decision.to_dict(), ensure_ascii=False) + "\n")

    def latest_for(self, proposal_id: str) -> Decision | None:
        if not self._file.exists():
            return None
        found: Decision | None = None
        for line in self._file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("proposal_id") == proposal_id:
                found = Decision(
                    proposal_id=proposal_id, outcome=data["outcome"],
                    approvals=[], rejection=None,
                    conditions=data.get("conditions", []),
                    evidence_id=data.get("evidence_id", ""))
        return found
