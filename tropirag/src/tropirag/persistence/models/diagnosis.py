"""Table ORM `diagnoses` — hypothèses différentielles hiérarchisées par cas."""
from __future__ import annotations

import time

from tropirag.persistence.models.base import Column

DIAGNOSIS_TABLE = "diagnoses"

DIAGNOSIS_COLUMNS = [
    Column("diagnosis_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("disease_code", "TEXT", nullable=False, index=True),
    Column("probability", "REAL"),
    Column("rank", "INTEGER"),
    Column("layer", "TEXT", default="rules"),    # rules | ai
    Column("rationale", "TEXT"),
    Column("created_at", "TEXT"),
]


def rows_from_differentials(case_id: str, differentials: list[dict],
                            layer: str = "rules") -> list[dict]:
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    rows = []
    for i, d in enumerate(differentials or []):
        if isinstance(d, dict):
            rows.append({
                "diagnosis_id": f"diag-{case_id}-{i:03d}",
                "case_id": case_id,
                "disease_code": d.get("disease") or d.get("disease_code") or "unknown",
                "probability": d.get("probability") or d.get("score"),
                "rank": i + 1,
                "layer": layer,
                "rationale": d.get("rationale") or d.get("reason"),
                "created_at": now,
            })
    return rows


def to_domain(row) -> dict:
    return {"disease": row["disease_code"], "probability": row["probability"],
            "rank": row["rank"], "layer": row["layer"],
            "rationale": row["rationale"]}
