"""Audit trail chaîné SHA-256, append-only (WORM V1 sur filesystem).

Chaque enregistrement porte `previous_hash` ; altérer une ligne casse toute
la chaîne (vérifié par verify_chain). Cohérent avec l'ADR plateforme 0021
(medisuite_core.audit_chain) mais autonome pour le control plane.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

GENESIS = "0" * 64


def _digest(record: dict[str, Any], previous_hash: str) -> str:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((previous_hash + payload).encode("utf-8")).hexdigest()


class AuditChain:
    def __init__(self, file_path: Path) -> None:
        self._path = Path(file_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, actor: str, **payload: Any) -> dict[str, Any]:
        previous = self.last_hash()
        record = {"event": event, "actor": actor, "timestamp": payload.pop(
            "timestamp", None) or _now(), **payload}
        entry = {"record": record, "previous_hash": previous,
                 "hash": _digest(record, previous)}
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def entries(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        return [json.loads(line) for line in
                self._path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def last_hash(self) -> str:
        entries = self.entries()
        return entries[-1]["hash"] if entries else GENESIS

    def verify_chain(self) -> tuple[bool, int]:
        """(intacte, première ligne corrompue ou -1)."""
        previous = GENESIS
        for i, entry in enumerate(self.entries()):
            expected = _digest(entry["record"], entry["previous_hash"])
            if entry["previous_hash"] != previous or entry["hash"] != expected:
                return False, i
            previous = entry["hash"]
        return True, -1


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
