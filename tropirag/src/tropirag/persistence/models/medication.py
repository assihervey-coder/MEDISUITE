"""Table ORM `medications` — contraintes et statuts médicamenteux par cas."""
from __future__ import annotations

from tropirag.persistence.models.base import Column

MEDICATION_TABLE = "medications"

MEDICATION_COLUMNS = [
    Column("medication_id", "TEXT", primary_key=True),
    Column("case_id", "TEXT", nullable=False, index=True),
    Column("drug_code", "TEXT", nullable=False, index=True),
    Column("status", "TEXT", default="recommended"),  # recommended | blocked | constrained
    Column("reason", "TEXT"),
    Column("source", "TEXT", default="rules"),        # rules | evidence
]


def rows_from_medication_constraints(case_id: str, constraints: list[dict]) -> list[dict]:
    """Contraintes médicamenteuses (sorties du moteur de règles) → lignes."""
    rows = []
    for i, c in enumerate(constraints or []):
        if isinstance(c, dict):
            rows.append({
                "medication_id": f"med-{case_id}-{i:03d}",
                "case_id": case_id,
                "drug_code": c.get("drug") or c.get("code") or "unknown",
                "status": c.get("status") or ("blocked" if c.get("blocked") else "constrained"),
                "reason": c.get("reason") or c.get("message"),
                "source": c.get("source", "rules"),
            })
    return rows


def to_domain(row) -> dict:
    return {"drug": row["drug_code"], "status": row["status"],
            "reason": row["reason"], "source": row["source"]}
