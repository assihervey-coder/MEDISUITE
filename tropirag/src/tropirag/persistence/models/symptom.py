"""Table ORM `symptoms` — symptômes normalisés par cas."""
from __future__ import annotations

from tropirag.persistence.models.base import Column

SYMPTOM_TABLE = "symptoms"

SYMPTOM_COLUMNS = [
    Column("symptom_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("code", "TEXT", nullable=False, index=True),
    Column("severity", "TEXT"),
    Column("onset_date", "TEXT"),
    Column("raw_text", "TEXT"),       # saisie d'origine (audit)
]


def rows_from_symptoms(case_id: str, payload: dict) -> list[dict]:
    """payload.symptoms → lignes symptoms.

    Accepte liste de codes, d'objets {code, severity, onset}, ou texte libre.
    """
    raw = payload.get("symptoms") or []
    if isinstance(raw, str):
        raw = [{"code": None, "raw_text": raw}]
    rows: list[dict] = []
    for i, item in enumerate(raw):
        if isinstance(item, str):
            rows.append(_row(case_id, i, code=item))
        elif isinstance(item, dict):
            rows.append(_row(case_id, i, code=item.get("code"),
                             severity=item.get("severity"),
                             onset=item.get("onset_date") or item.get("onset"),
                             raw_text=item.get("raw") or item.get("text")))
    return rows


def _row(case_id: str, i: int, code: str | None, severity: str | None = None,
         onset: str | None = None, raw_text: str | None = None) -> dict:
    return {
        "symptom_id": f"sym-{case_id}-{i:03d}",
        "case_id": case_id, "code": code, "severity": severity,
        "onset_date": onset, "raw_text": raw_text,
    }


def to_domain(row) -> dict:
    return {"code": row["code"], "severity": row["severity"],
            "onset_date": row["onset_date"], "raw": row["raw_text"]}
