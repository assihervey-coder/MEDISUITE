"""Table ORM `audit_events_orm` — journal d'audit relationnel (complément du legacy)."""
from __future__ import annotations

import json

from tropirag.persistence.models.base import Column

AUDIT_EVENT_TABLE = "audit_events_orm"

AUDIT_EVENT_COLUMNS = [
    Column("audit_id", "TEXT", primary_key=True),
    Column("ts", "TEXT", nullable=False, index=True),
    Column("event", "TEXT", nullable=False, index=True),
    Column("category", "TEXT", index=True),     # clinical | safety | ai | system
    Column("case_id", "TEXT", index=True),
    Column("actor", "TEXT"),
    Column("payload_json", "TEXT"),
]


def row_from_audit(audit_id: str, event: str, ts: str, payload: dict | None = None,
                   category: str = "system", case_id: str | None = None,
                   actor: str = "system") -> dict:
    return {
        "audit_id": audit_id, "ts": ts, "event": event, "category": category,
        "case_id": case_id, "actor": actor,
        "payload_json": json.dumps(payload or {}, ensure_ascii=False),
    }


def to_domain(row) -> dict:
    return {"audit_id": row["audit_id"], "ts": row["ts"], "event": row["event"],
            "category": row["category"], "case_id": row["case_id"],
            "actor": row["actor"], "payload": json.loads(row["payload_json"] or "{}")}
