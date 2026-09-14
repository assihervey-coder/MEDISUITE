"""Dépôt patients — vues ORM normalisées (patients, symptômes liés)."""
from __future__ import annotations

import json

from tropirag.persistence.database import Database


class PatientRepository:

    def __init__(self, db: Database) -> None:
        self.db = db

    # --- vue legacy (JSON dans cases) --------------------------------------
    def for_case(self, case_id: str) -> dict | None:
        rows = self.db.query("SELECT patient_json FROM cases WHERE case_id = ?", (case_id,))
        if not rows:
            return None
        return json.loads(rows[0]["patient_json"])

    # --- vues ORM normalisées ----------------------------------------------
    def row_for_case(self, case_id: str) -> dict | None:
        rows = self.db.query("SELECT * FROM patients WHERE case_id = ?", (case_id,))
        if not rows:
            return None
        r = rows[0]
        return {"age": r["age_years"], "age_months": r["age_months"],
                "sex": r["sex"], "pregnant": bool(r["pregnant"]),
                "gestational_age_weeks": r["gestational_age_weeks"],
                "conditions": json.loads(r["conditions_json"] or "[]"),
                "region": r["region"], "district": r["district"]}

    def pregnant_cases(self) -> list[dict]:
        rows = self.db.query(
            "SELECT p.case_id, p.gestational_age_weeks, c.created_at "
            "FROM patients p JOIN clinical_cases c ON c.case_id = p.case_id "
            "WHERE p.pregnant = 1 ORDER BY c.created_at DESC")
        return [dict(r) for r in rows]

    def by_region(self, region: str) -> list[dict]:
        rows = self.db.query(
            "SELECT p.*, c.created_at FROM patients p "
            "JOIN clinical_cases c ON c.case_id = p.case_id "
            "WHERE p.region = ? ORDER BY c.created_at DESC", (region,))
        return [{"case_id": r["case_id"], "age": r["age_years"], "sex": r["sex"],
                 "pregnant": bool(r["pregnant"]), "district": r["district"]}
                for r in rows]

    def with_condition(self, condition: str) -> list[dict]:
        rows = self.db.query(
            "SELECT case_id, conditions_json FROM patients "
            "WHERE conditions_json LIKE ?", (f'%"{condition}"%',))
        out = []
        for r in rows:
            conds = json.loads(r["conditions_json"] or "[]")
            if condition in conds:
                out.append({"case_id": r["case_id"], "conditions": conds})
        return out

    def age_distribution(self) -> dict:
        rows = self.db.query(
            "SELECT age_years, COUNT(*) AS n FROM patients "
            "WHERE age_years IS NOT NULL GROUP BY age_years ORDER BY age_years")
        return {int(r["age_years"]): int(r["n"]) for r in rows}
