"""Table ORM `clinical_cases` — version relationnelle du cas + copie JSON d'audit."""
from __future__ import annotations

import json
import time

from tropirag.persistence.models.base import Column

CASE_TABLE = "clinical_cases"

CASE_COLUMNS = [
    Column("case_id", "TEXT", primary_key=True),
    Column("created_at", "TEXT", nullable=False, index=True),
    Column("patient_id", "TEXT", nullable=False),
    Column("region", "TEXT", index=True),
    Column("district", "TEXT", index=True),
    Column("chief_complaint", "TEXT"),
    Column("symptoms_count", "INTEGER", default=0),
    Column("payload_json", "TEXT", nullable=False),   # copie immuable d'audit
]


def row_from_case(case_id: str, patient: dict, payload: dict,
                  created_at: str | None = None) -> dict:
    symptoms = payload.get("symptoms") or []
    if isinstance(symptoms, str):
        symptoms = [symptoms]
    return {
        "case_id": case_id,
        "created_at": created_at or time.strftime("%Y-%m-%dT%H:%M:%S"),
        "patient_id": f"pat-{case_id}",
        "region": (patient or {}).get("region"),
        "district": (patient or {}).get("district"),
        "chief_complaint": payload.get("chief_complaint"),
        "symptoms_count": len(symptoms),
        "payload_json": json.dumps(payload, ensure_ascii=False),
    }


def to_domain(row) -> dict:
    return {
        "case_id": row["case_id"], "created_at": row["created_at"],
        "patient_id": row["patient_id"], "region": row["region"],
        "district": row["district"],
        "payload": json.loads(row["payload_json"]),
    }
