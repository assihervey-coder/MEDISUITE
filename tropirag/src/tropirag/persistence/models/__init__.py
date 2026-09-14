"""Modèles ORM — registre des 12 tables normalisées du schéma TropiRAG.

Ordre de création respectant les clés étrangères :
    patient → clinical_case → travel / symptom
    → diagnosis / diagnostic_test / medication / evidence_usage
    → source → evidence_unit → models_registry → inference → audit_event

Chaque module expose : TABLE, COLUMNS, DDL, INDEXES, row_from_* / to_domain.
"""
from __future__ import annotations

import sqlite3

from tropirag.persistence.models.base import build_ddl, index_ddl
from tropirag.persistence.models.patient import PATIENT_COLUMNS, PATIENT_TABLE, row_from_patient
from tropirag.persistence.models.clinical_case import (
    CASE_COLUMNS,
    CASE_TABLE,
    row_from_case,
)
from tropirag.persistence.models.travel import TRAVEL_COLUMNS, TRAVEL_TABLE, rows_from_travel
from tropirag.persistence.models.symptom import SYMPTOM_COLUMNS, SYMPTOM_TABLE, rows_from_symptoms
from tropirag.persistence.models.diagnosis import (
    DIAGNOSIS_COLUMNS,
    DIAGNOSIS_TABLE,
    rows_from_differentials,
)
from tropirag.persistence.models.diagnostic_test import (
    DIAGNOSTIC_TEST_COLUMNS,
    DIAGNOSTIC_TEST_TABLE,
    rows_from_tests,
)
from tropirag.persistence.models.medication import (
    MEDICATION_COLUMNS,
    MEDICATION_TABLE,
    rows_from_medication_constraints,
)
from tropirag.persistence.models.evidence import (
    EVIDENCE_COLUMNS,
    EVIDENCE_TABLE,
    rows_from_evidence_usage,
)
from tropirag.persistence.models.source import SOURCE_COLUMNS, SOURCE_TABLE, row_from_source
from tropirag.persistence.models.model import MODEL_COLUMNS, MODEL_TABLE, row_from_model_meta
from tropirag.persistence.models.inference import (
    INFERENCE_COLUMNS,
    INFERENCE_TABLE,
    row_from_inference,
)
from tropirag.persistence.models.audit_event import (
    AUDIT_EVENT_COLUMNS,
    AUDIT_EVENT_TABLE,
    row_from_audit,
)

# registre ordonné (FK parents avant enfants)
ORM_TABLES: list[tuple[str, list]] = [
    (PATIENT_TABLE, PATIENT_COLUMNS),
    (CASE_TABLE, CASE_COLUMNS),
    (TRAVEL_TABLE, TRAVEL_COLUMNS),
    (SYMPTOM_TABLE, SYMPTOM_COLUMNS),
    (DIAGNOSIS_TABLE, DIAGNOSIS_COLUMNS),
    (DIAGNOSTIC_TEST_TABLE, DIAGNOSTIC_TEST_COLUMNS),
    (MEDICATION_TABLE, MEDICATION_COLUMNS),
    (EVIDENCE_TABLE, EVIDENCE_COLUMNS),
    (SOURCE_TABLE, SOURCE_COLUMNS),
    (MODEL_TABLE, MODEL_COLUMNS),
    (INFERENCE_TABLE, INFERENCE_COLUMNS),
    (AUDIT_EVENT_TABLE, AUDIT_EVENT_COLUMNS),
]


def create_orm_schema(conn: sqlite3.Connection) -> None:
    """Crée les 12 tables + index (idempotent)."""
    for table, columns in ORM_TABLES:
        conn.execute(build_ddl(table, columns))
        for stmt in index_ddl(table, columns):
            conn.execute(stmt)


def orm_schema_sql() -> str:
    """Script SQL complet du schéma ORM (migrations initiales)."""
    parts: list[str] = []
    for table, columns in ORM_TABLES:
        parts.append(build_ddl(table, columns) + ";")
        parts.extend(s + ";" for s in index_ddl(table, columns))
    return "\n".join(parts)


def orm_tables() -> list[str]:
    return [t for t, _ in ORM_TABLES]
