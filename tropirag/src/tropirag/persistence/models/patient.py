"""Table ORM `patients` — instantané normalisé du patient par cas.

Chaque cas porte l'instantané du patient au moment de l'analyse (le patient
terrain n'a pas d'identifiant national dans V1 — confidentialité par design).
"""
from __future__ import annotations

import json
import time

from tropirag.persistence.models.base import Column

PATIENT_TABLE = "patients"

PATIENT_COLUMNS = [
    Column("patient_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("age_years", "INTEGER"),
    Column("age_months", "INTEGER"),
    Column("sex", "TEXT"),
    Column("pregnant", "INTEGER", default=0),
    Column("gestational_age_weeks", "INTEGER"),
    Column("conditions_json", "TEXT"),
    Column("region", "TEXT", index=True),
    Column("district", "TEXT", index=True),
    Column("created_at", "TEXT"),
]


def row_from_patient(case_id: str, patient: dict) -> dict:
    """payload.patient → ligne patients."""
    conditions = patient.get("conditions") or patient.get("has_condition") or []
    if isinstance(conditions, str):
        conditions = [conditions]
    return {
        "patient_id": f"pat-{case_id}",
        "case_id": case_id,
        "age_years": patient.get("age"),
        "age_months": patient.get("age_months"),
        "sex": patient.get("sex"),
        "pregnant": 1 if patient.get("pregnant") else 0,
        "gestational_age_weeks": patient.get("gestational_age_weeks"),
        "conditions_json": json.dumps(conditions, ensure_ascii=False),
        "region": patient.get("region"),
        "district": patient.get("district"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def to_domain(row) -> dict:
    """ligne patients → dictionnaire domaine."""
    return {
        "age": row["age_years"], "age_months": row["age_months"],
        "sex": row["sex"], "pregnant": bool(row["pregnant"]),
        "gestational_age_weeks": row["gestational_age_weeks"],
        "conditions": json.loads(row["conditions_json"] or "[]"),
        "region": row["region"], "district": row["district"],
    }
