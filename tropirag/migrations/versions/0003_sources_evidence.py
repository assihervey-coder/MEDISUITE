"""0003 — sources institutionnelles + traçabilité des preuves.

Revision ID: 0003_sources_evidence
Revises: 0002_clinical_analyses
"""
from __future__ import annotations

import sqlite3

REVISION = "0003_sources_evidence"
DOWN_REVISION = "0002_clinical_analyses"

UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    authority TEXT NOT NULL, title TEXT, publisher TEXT,
    edition_date TEXT, jurisdiction TEXT, url TEXT,
    document_type TEXT DEFAULT 'guideline'
);
CREATE INDEX IF NOT EXISTS idx_sources_authority ON sources(authority);
CREATE INDEX IF NOT EXISTS idx_sources_edition_date ON sources(edition_date);
CREATE INDEX IF NOT EXISTS idx_sources_jurisdiction ON sources(jurisdiction);

CREATE TABLE IF NOT EXISTS evidence_usage (
    evidence_id INTEGER PRIMARY KEY,
    case_id TEXT, unit_id TEXT NOT NULL, score REAL, used_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_evidence_usage_case_id ON evidence_usage(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_usage_unit_id ON evidence_usage(unit_id);
"""

DOWNGRADE_SQL = """
DROP INDEX IF EXISTS idx_evidence_usage_unit_id;
DROP INDEX IF EXISTS idx_evidence_usage_case_id;
DROP TABLE IF EXISTS evidence_usage;
DROP INDEX IF EXISTS idx_sources_jurisdiction;
DROP INDEX IF EXISTS idx_sources_edition_date;
DROP INDEX IF EXISTS idx_sources_authority;
DROP TABLE IF EXISTS sources;
"""


def upgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(UPGRADE_SQL)


def downgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(DOWNGRADE_SQL)
