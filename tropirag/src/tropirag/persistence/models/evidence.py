"""Table ORM `evidence_usage` — traçabilité unités de preuve × cas."""
from __future__ import annotations

from tropirag.persistence.models.base import Column

EVIDENCE_TABLE = "evidence_usage"

EVIDENCE_COLUMNS = [
    Column("evidence_id", "INTEGER", primary_key=True),
    Column("case_id", "TEXT", index=True),
    Column("unit_id", "TEXT", nullable=False, index=True),
    Column("score", "REAL"),
    Column("used_at", "TEXT"),
]


def rows_from_evidence_usage(case_id: str, pack_units: list[tuple[str, float]]) -> list[dict]:
    """(unit_id, score) du pack → lignes evidence_usage."""
    import time

    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    return [{"case_id": case_id, "unit_id": uid, "score": round(float(s), 4),
             "used_at": now} for uid, s in pack_units]


def to_domain(row) -> dict:
    return {"case_id": row["case_id"], "unit_id": row["unit_id"],
            "score": row["score"], "used_at": row["used_at"]}
