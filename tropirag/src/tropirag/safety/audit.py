"""Piste d'audit immuable (JSONL + SQLite)."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from tropirag.core.identifiers import new_id


class AuditTrail:
    """Journal append-only de tous les événements de décision."""

    def __init__(self, log_dir: Path | None = None) -> None:
        from tropirag.core.config import RUNTIME_DIR

        self.log_dir = Path(log_dir or (RUNTIME_DIR / "logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.log_dir / f"audit-{time.strftime('%Y%m%d')}.jsonl"
        self._memory: list[dict] = []

    def record(self, event: str, payload: dict[str, Any] | None = None) -> dict:
        entry = {
            "audit_id": new_id("audit"),
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event": event,
            "payload": payload or {},
        }
        self._memory.append(entry)
        with open(self._file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def recent(self, n: int = 50) -> list[dict]:
        return self._memory[-n:]

    def size(self) -> int:
        return len(self._memory)
