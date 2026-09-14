"""Table ORM `travel` — historique de voyage et expositions par cas."""
from __future__ import annotations

import json

from tropirag.persistence.models.base import Column

TRAVEL_TABLE = "travel"

TRAVEL_COLUMNS = [
    Column("travel_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("countries_json", "TEXT"),
    Column("regions_json", "TEXT"),
    Column("districts_json", "TEXT"),
    Column("exposures_json", "TEXT"),
    Column("departure_date", "TEXT", index=True),
    Column("return_date", "TEXT", index=True),
]


def rows_from_travel(case_id: str, payload: dict) -> list[dict]:
    """payload.travel → lignes travel (une par séjour déclaré, sinon une)."""
    travel = payload.get("travel") or {}
    trips = travel.get("trips")
    if not trips:
        return [_row(case_id, 1, travel)]
    return [_row(case_id, i + 1, trip) for i, trip in enumerate(trips)]


def _row(case_id: str, idx: int, t: dict) -> dict:
    return {
        "travel_id": f"trv-{case_id}-{idx:02d}",
        "case_id": case_id,
        "countries_json": json.dumps(t.get("countries", []), ensure_ascii=False),
        "regions_json": json.dumps(t.get("regions", []), ensure_ascii=False),
        "districts_json": json.dumps(t.get("districts", []), ensure_ascii=False),
        "exposures_json": json.dumps(t.get("exposures", []), ensure_ascii=False),
        "departure_date": t.get("departure_date"),
        "return_date": t.get("return_date"),
    }


def to_domain(row) -> dict:
    return {
        "travel_id": row["travel_id"], "case_id": row["case_id"],
        "countries": json.loads(row["countries_json"] or "[]"),
        "regions": json.loads(row["regions_json"] or "[]"),
        "districts": json.loads(row["districts_json"] or "[]"),
        "exposures": json.loads(row["exposures_json"] or "[]"),
        "departure_date": row["departure_date"], "return_date": row["return_date"],
    }
