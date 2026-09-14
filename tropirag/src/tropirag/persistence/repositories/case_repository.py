"""Dépôt des cas cliniques — double écriture legacy (audit JSON) + ORM normalisé.

Tables alimentées à chaque save :
    cases / analyses (legacy, append-only, compat descendante)
    patients, clinical_cases, travel, symptoms, diagnoses,
    diagnostic_tests, medications (ORM, vues relationnelles)
"""
from __future__ import annotations

import json
import time

from tropirag.persistence.database import Database
from tropirag.persistence.models.clinical_case import row_from_case
from tropirag.persistence.models.diagnosis import rows_from_differentials
from tropirag.persistence.models.diagnostic_test import rows_from_tests
from tropirag.persistence.models.medication import rows_from_medication_constraints
from tropirag.persistence.models.patient import row_from_patient
from tropirag.persistence.models.symptom import rows_from_symptoms
from tropirag.persistence.models.travel import rows_from_travel


class CaseRepository:

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Écriture (legacy + ORM)
    # ------------------------------------------------------------------
    def save_case(self, case_id: str, patient: dict, payload: dict) -> None:
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        # --- legacy (audit JSON immuable) ---------------------------------
        self.db.execute(
            "INSERT OR REPLACE INTO cases (case_id, created_at, patient_json, payload_json) VALUES (?,?,?,?)",
            (case_id, now,
             json.dumps(patient, ensure_ascii=False), json.dumps(payload, ensure_ascii=False)))
        # --- ORM normalisé -------------------------------------------------
        conn = self.db.connection
        conn.execute("DELETE FROM patients WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM clinical_cases WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM travel WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM symptoms WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM diagnostic_tests WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM diagnoses WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM medications WHERE case_id = ?", (case_id,))
        from tropirag.persistence.models.base import build_ddl  # noqa: F401

        def _insert(table: str, row: dict) -> None:
            keys = list(row)
            conn.execute(
                f"INSERT OR REPLACE INTO {table} ({', '.join(keys)}) "
                f"VALUES ({', '.join('?' * len(keys))})",
                tuple(row[k] for k in keys))

        _insert("patients", row_from_patient(case_id, patient or {}))
        _insert("clinical_cases", row_from_case(case_id, patient or {}, payload or {},
                                                created_at=now))
        for row in rows_from_travel(case_id, payload or {}):
            _insert("travel", row)
        for row in rows_from_symptoms(case_id, payload or {}):
            _insert("symptoms", row)
        for row in rows_from_tests(case_id, payload or {}):
            _insert("diagnostic_tests", row)
        self.db.commit()

    def get_case(self, case_id: str) -> dict | None:
        rows = self.db.query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        if not rows:
            return None
        r = rows[0]
        return {"case_id": r["case_id"], "created_at": r["created_at"],
                "patient": json.loads(r["patient_json"]),
                "payload": json.loads(r["payload_json"])}

    # ------------------------------------------------------------------
    def save_analysis(self, case_id: str, urgency: str, severity: str,
                      differentials: list[dict], matched_rules: list[str],
                      ai_layer: str, refusal: str | None) -> int:
        cur = self.db.execute(
            "INSERT INTO analyses (case_id, created_at, urgency, severity, differentials_json,"
            " matched_rules_json, ai_layer, refusal) VALUES (?,?,?,?,?,?,?,?)",
            (case_id, time.strftime("%Y-%m-%dT%H:%M:%S"), urgency, severity,
             json.dumps(differentials, ensure_ascii=False),
             json.dumps(matched_rules), ai_layer, refusal))
        # --- ORM : hypothèses différentielles normalisées --------------------
        conn = self.db.connection
        conn.execute("DELETE FROM diagnoses WHERE case_id = ?", (case_id,))
        for row in rows_from_differentials(case_id, differentials):
            keys = list(row)
            conn.execute(
                f"INSERT OR REPLACE INTO diagnoses ({', '.join(keys)}) "
                f"VALUES ({', '.join('?' * len(keys))})",
                tuple(row[k] for k in keys))
        self.db.commit()
        return cur.lastrowid or 0

    def save_medication_constraints(self, case_id: str,
                                    constraints: list[dict]) -> int:
        """Contraintes médicamenteuses → table medications."""
        conn = self.db.connection
        conn.execute("DELETE FROM medications WHERE case_id = ?", (case_id,))
        for row in rows_from_medication_constraints(case_id, constraints):
            keys = list(row)
            conn.execute(
                f"INSERT OR REPLACE INTO medications ({', '.join(keys)}) "
                f"VALUES ({', '.join('?' * len(keys))})",
                tuple(row[k] for k in keys))
        self.db.commit()
        return len(constraints)

    # ------------------------------------------------------------------
    # Lectures ORM relationnelles
    # ------------------------------------------------------------------
    def recent_analyses(self, limit: int = 20) -> list[dict]:
        rows = self.db.query(
            "SELECT a.*, c.created_at AS case_created FROM analyses a "
            "LEFT JOIN cases c ON c.case_id = a.case_id "
            "ORDER BY a.id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]

    def analyses_between(self, start_iso: str, end_iso: str) -> list[dict]:
        """Analyses créées dans [start_iso, end_iso] inclus — export DHIS2."""
        rows = self.db.query(
            "SELECT * FROM analyses WHERE created_at >= ? AND created_at <= ? "
            "ORDER BY id", (start_iso, end_iso + "T23:59:59"))
        return [dict(r) for r in rows]

    # --- vues ORM ----------------------------------------------------------
    def case_symptoms(self, case_id: str) -> list[dict]:
        rows = self.db.query("SELECT * FROM symptoms WHERE case_id = ? ORDER BY code",
                             (case_id,))
        return [{"code": r["code"], "severity": r["severity"]} for r in rows]

    def case_travel(self, case_id: str) -> list[dict]:
        rows = self.db.query("SELECT * FROM travel WHERE case_id = ?", (case_id,))
        out = []
        for r in rows:
            out.append({"countries": json.loads(r["countries_json"] or "[]"),
                        "exposures": json.loads(r["exposures_json"] or "[]"),
                        "departure_date": r["departure_date"],
                        "return_date": r["return_date"]})
        return out

    def case_diagnoses(self, case_id: str) -> list[dict]:
        rows = self.db.query(
            "SELECT * FROM diagnoses WHERE case_id = ? ORDER BY rank", (case_id,))
        return [{"disease": r["disease_code"], "probability": r["probability"],
                 "rank": r["rank"], "layer": r["layer"]} for r in rows]

    def symptoms_by_code(self, code: str) -> list[dict]:
        rows = self.db.query(
            "SELECT s.*, c.region FROM symptoms s "
            "LEFT JOIN clinical_cases c ON c.case_id = s.case_id "
            "WHERE s.code = ? ORDER BY c.created_at DESC LIMIT 50", (code,))
        return [{"case_id": r["case_id"], "severity": r["severity"],
                 "region": r["region"]} for r in rows]

    def cases_by_region(self, region: str) -> list[dict]:
        rows = self.db.query(
            "SELECT * FROM clinical_cases WHERE region = ? ORDER BY created_at DESC",
            (region,))
        return [{"case_id": r["case_id"], "created_at": r["created_at"],
                 "symptoms_count": r["symptoms_count"]} for r in rows]

    def stats(self) -> dict:
        rows = self.db.query("SELECT COUNT(*) AS n FROM cases")
        cases = rows[0]["n"] if rows else 0
        rows = self.db.query("SELECT urgency, COUNT(*) AS n FROM analyses GROUP BY urgency")
        return {"cases": cases, "by_urgency": {r["urgency"]: r["n"] for r in rows}}

    def orm_stats(self) -> dict:
        """Compteurs par table ORM — observabilité du schéma normalisé."""
        out: dict[str, int] = {}
        for t in ("patients", "clinical_cases", "travel", "symptoms", "diagnoses",
                  "diagnostic_tests", "medications", "evidence_usage", "sources",
                  "models_registry", "inferences", "audit_events_orm"):
            row = self.db.query(f"SELECT COUNT(*) AS n FROM {t}")
            out[t] = row[0]["n"] if row else 0
        return out
