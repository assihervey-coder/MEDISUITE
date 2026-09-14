"""Table ORM `diagnostic_tests` — examens demandés/résultats par cas."""
from __future__ import annotations

from tropirag.persistence.models.base import Column

DIAGNOSTIC_TEST_TABLE = "diagnostic_tests"

DIAGNOSTIC_TEST_COLUMNS = [
    Column("test_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("code", "TEXT", nullable=False, index=True),
    Column("result", "TEXT"),
    Column("result_detail", "TEXT"),
    Column("performed_at", "TEXT"),
]


def rows_from_tests(case_id: str, payload: dict) -> list[dict]:
    """payload.lab_results / tests → lignes diagnostic_tests."""
    raw = payload.get("lab_results") or payload.get("tests") or []
    if isinstance(raw, str):
        raw = [{"code": raw}]
    rows: list[dict] = []
    for i, item in enumerate(raw):
        if isinstance(item, str):
            rows.append({"test_id": f"tst-{case_id}-{i:03d}", "case_id": case_id,
                         "code": item, "result": None, "result_detail": None,
                         "performed_at": None})
        elif isinstance(item, dict):
            code = item.get("code") or item.get("test") or item.get("name")
            rows.append({
                "test_id": f"tst-{case_id}-{i:03d}", "case_id": case_id,
                "code": code, "result": item.get("result"),
                "result_detail": item.get("detail") or item.get("value"),
                "performed_at": item.get("performed_at") or item.get("date"),
            })
    return rows


def to_domain(row) -> dict:
    return {"code": row["code"], "result": row["result"],
            "detail": row["result_detail"], "performed_at": row["performed_at"]}
