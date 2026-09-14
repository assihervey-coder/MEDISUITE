"""0001 — schéma initial : patients, clinical_cases, travel, symptoms.

Migration fondatrice de l'ORM multi-tables. Idempotente (IF NOT EXISTS) :
cohabite avec les tables legacy créées par persistence.database.SCHEMA.

Revision ID: 0001_domain_core
Revises: None
"""
from __future__ import annotations

import sqlite3

REVISION = "0001_domain_core"
DOWN_REVISION = None

UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    age_years INTEGER, age_months INTEGER, sex TEXT,
    pregnant INTEGER DEFAULT 0, gestational_age_weeks INTEGER,
    conditions_json TEXT, region TEXT, district TEXT, created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_patients_case_id ON patients(case_id);
CREATE INDEX IF NOT EXISTS idx_patients_region ON patients(region);
CREATE INDEX IF NOT EXISTS idx_patients_district ON patients(district);

CREATE TABLE IF NOT EXISTS clinical_cases (
    case_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    region TEXT, district TEXT,
    chief_complaint TEXT, symptoms_count INTEGER DEFAULT 0,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clinical_cases_created_at ON clinical_cases(created_at);
CREATE INDEX IF NOT EXISTS idx_clinical_cases_region ON clinical_cases(region);
CREATE INDEX IF NOT EXISTS idx_clinical_cases_district ON clinical_cases(district);

CREATE TABLE IF NOT EXISTS travel (
    travel_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    countries_json TEXT, regions_json TEXT, districts_json TEXT,
    exposures_json TEXT, departure_date TEXT, return_date TEXT
);
CREATE INDEX IF NOT EXISTS idx_travel_case_id ON travel(case_id);
CREATE INDEX IF NOT EXISTS idx_travel_departure_date ON travel(departure_date);
CREATE INDEX IF NOT EXISTS idx_travel_return_date ON travel(return_date);

CREATE TABLE IF NOT EXISTS symptoms (
    symptom_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    code TEXT NOT NULL, severity TEXT, onset_date TEXT, raw_text TEXT
);
CREATE INDEX IF NOT EXISTS idx_symptoms_case_id ON symptoms(case_id);
CREATE INDEX IF NOT EXISTS idx_symptoms_code ON symptoms(code);
"""

DOWNGRADE_SQL = """
DROP INDEX IF EXISTS idx_symptoms_code;
DROP INDEX IF EXISTS idx_symptoms_case_id;
DROP TABLE IF EXISTS symptoms;
DROP INDEX IF EXISTS idx_travel_return_date;
DROP INDEX IF EXISTS idx_travel_departure_date;
DROP INDEX IF EXISTS idx_travel_case_id;
DROP TABLE IF EXISTS travel;
DROP INDEX IF EXISTS idx_clinical_cases_district;
DROP INDEX IF EXISTS idx_clinical_cases_region;
DROP INDEX IF EXISTS idx_clinical_cases_created_at;
DROP TABLE IF EXISTS clinical_cases;
DROP INDEX IF EXISTS idx_patients_district;
DROP INDEX IF EXISTS idx_patients_region;
DROP INDEX IF EXISTS idx_patients_case_id;
DROP TABLE IF EXISTS patients;
"""


def upgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(UPGRADE_SQL)


def downgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(DOWNGRADE_SQL)
