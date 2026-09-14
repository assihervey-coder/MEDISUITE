"""Dépôt des événements d'audit."""
from __future__ import annotations

import json
import time

from tropirag.persistence.database import Database


class AuditRepository:

    def __init__(self, db: Database) -> None:
        self.db = db

    def record(self, audit_id: str, event: str, payload: dict) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO audit_events (audit_id, ts, event, payload_json) VALUES (?,?,?,?)",
            (audit_id, time.strftime("%Y-%m-%dT%H:%M:%S"), event,
             json.dumps(payload, ensure_ascii=False, default=str)))

    def recent(self, limit: int = 50) -> list[dict]:
        rows = self.db.query(
            "SELECT * FROM audit_events ORDER BY ts DESC, audit_id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]
