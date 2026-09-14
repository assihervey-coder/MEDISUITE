"""File d'attente offline — les payloads attendent le réseau en toute sécurité.

Persistée en JSON (runtime/state/dhis2_queue.json) : chaque entrée garde son
payload, son statut (pending/sent/failed) et son nombre de tentatives.
C'est le pont entre le district à connectivité intermittente et le serveur
DHIS2 central du MSP-CI.
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path


class OfflineQueue:
    """File JSON persistée — thread-safe, tolérante aux pannes."""

    def __init__(self, path: Path, max_entries: int = 5000) -> None:
        self.path = Path(path)
        self.max_entries = max_entries
        self._lock = threading.Lock()
        self._entries: list[dict] = []
        self._load()

    # --- persistance ---------------------------------------------------------
    def _load(self) -> None:
        if self.path.exists():
            try:
                with open(self.path, encoding="utf-8") as fh:
                    self._entries = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._entries = []  # fichier corrompu → repartir propre
        else:
            self._entries = []

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self._entries, fh, ensure_ascii=False, indent=1)

    # --- opérations ------------------------------------------------------------
    def enqueue(self, payload: dict, meta: dict | None = None) -> dict:
        entry = {
            "id": uuid.uuid4().hex[:12],
            "queued_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "pending",
            "attempts": 0,
            "payload": payload,
            "meta": meta or {},
        }
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self.max_entries:
                self._entries = [e for e in self._entries if e["status"] != "sent"]
                self._entries = self._entries[-self.max_entries:]
            self._flush()
        return entry

    def pending(self) -> list[dict]:
        return [e for e in self._entries if e["status"] == "pending"]

    def mark(self, entry_id: str, status: str, note: str = "") -> None:
        with self._lock:
            for e in self._entries:
                if e["id"] == entry_id:
                    e["status"] = status
                    e["attempts"] = int(e.get("attempts", 0)) + 1
                    e["last_note"] = note
                    e["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                    break
            self._flush()

    def status_summary(self) -> dict:
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e["status"]] = counts.get(e["status"], 0) + 1
        return {
            "total": len(self._entries),
            "by_status": counts,
            "pending": counts.get("pending", 0),
            "path": str(self.path),
        }
