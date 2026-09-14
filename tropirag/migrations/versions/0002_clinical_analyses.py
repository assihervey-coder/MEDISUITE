"""0002 — analyses cliniques : diagnoses, diagnostic_tests, medications.

Revision ID: 0002_clinical_analyses
Revises: 0001_domain_core
"""
from __future__ import annotations

import sqlite3

REVISION = "0002_clinical_analyses"
DOWN_REVISION = "0001_domain_core"

UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    disease_code TEXT NOT NULL, probability REAL, "rank" INTEGER,
    layer TEXT DEFAULT 'rules', rationale TEXT, created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_diagnoses_case_id ON diagnoses(case_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_disease_code ON diagnoses(disease_code);

CREATE TABLE IF NOT EXISTS diagnostic_tests (
    test_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    code TEXT NOT NULL, result TEXT, result_detail TEXT, performed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_diagnostic_tests_case_id ON diagnostic_tests(case_id);
CREATE INDEX IF NOT EXISTS idx_diagnostic_tests_code ON diagnostic_tests(code);

CREATE TABLE IF NOT EXISTS medications (
    medication_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    drug_code TEXT NOT NULL, status TEXT DEFAULT 'recommended',
    reason TEXT, source TEXT DEFAULT 'rules'
);
CREATE INDEX IF NOT EXISTS idx_medications_case_id ON medications(case_id);
CREATE INDEX IF NOT EXISTS idx_medications_drug_code ON medications(drug_code);
"""

DOWNGRADE_SQL = """
DROP INDEX IF EXISTS idx_medications_drug_code;
DROP INDEX IF EXISTS idx_medications_case_id;
DROP TABLE IF EXISTS medications;
DROP INDEX IF EXISTS idx_diagnostic_tests_code;
DROP INDEX IF EXISTS idx_diagnostic_tests_case_id;
DROP TABLE IF EXISTS diagnostic_tests;
DROP INDEX IF EXISTS idx_diagnoses_disease_code;
DROP INDEX IF EXISTS idx_diagnoses_case_id;
DROP TABLE IF EXISTS diagnoses;
"""


def upgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(UPGRADE_SQL)


def downgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(DOWNGRADE_SQL)
