"""0004 — mesh IA : models_registry, inferences + audit relationnel.

Revision ID: 0004_ai_mesh_audit
Revises: 0003_sources_evidence
"""
from __future__ import annotations

import sqlite3

REVISION = "0004_ai_mesh_audit"
DOWN_REVISION = "0003_sources_evidence"

UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS models_registry (
    model_id TEXT PRIMARY KEY,
    display_name TEXT, family TEXT, gateway TEXT, vram_gb REAL,
    priority INTEGER, deployment TEXT,
    clinically_validated INTEGER DEFAULT 0,
    capabilities_json TEXT, health TEXT DEFAULT 'unknown'
);
CREATE INDEX IF NOT EXISTS idx_models_registry_family ON models_registry(family);

CREATE TABLE IF NOT EXISTS inferences (
    inference_id TEXT PRIMARY KEY,
    case_id TEXT, model_id TEXT, task TEXT,
    mode TEXT DEFAULT 'deterministic', status TEXT,
    latency_ms REAL, detail TEXT, created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_inferences_case_id ON inferences(case_id);
CREATE INDEX IF NOT EXISTS idx_inferences_model_id ON inferences(model_id);

CREATE TABLE IF NOT EXISTS audit_events_orm (
    audit_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL, event TEXT NOT NULL, category TEXT,
    case_id TEXT, actor TEXT, payload_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_events_orm_ts ON audit_events_orm(ts);
CREATE INDEX IF NOT EXISTS idx_audit_events_orm_event ON audit_events_orm(event);
CREATE INDEX IF NOT EXISTS idx_audit_events_orm_category ON audit_events_orm(category);
CREATE INDEX IF NOT EXISTS idx_audit_events_orm_case_id ON audit_events_orm(case_id);
"""

DOWNGRADE_SQL = """
DROP INDEX IF EXISTS idx_audit_events_orm_case_id;
DROP INDEX IF EXISTS idx_audit_events_orm_category;
DROP INDEX IF EXISTS idx_audit_events_orm_event;
DROP INDEX IF EXISTS idx_audit_events_orm_ts;
DROP TABLE IF EXISTS audit_events_orm;
DROP INDEX IF EXISTS idx_inferences_model_id;
DROP INDEX IF EXISTS idx_inferences_case_id;
DROP TABLE IF EXISTS inferences;
DROP INDEX IF EXISTS idx_models_registry_family;
DROP TABLE IF EXISTS models_registry;
"""


def upgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(UPGRADE_SQL)


def downgrade(conn: sqlite3.Connection) -> None:
    conn.executescript(DOWNGRADE_SQL)
