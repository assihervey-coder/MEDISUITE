"""Persistance SQLite — stdlib pure, schéma versionné, ORM multi-tables, repositories.

V1 : SQLite embarqué (single-node). L'interface repository permet de basculer
vers PostgreSQL sans toucher au domaine.

Schéma :
    - tables LEGACY (cases, analyses, evidence_usage, audit_events) — append-only
      audit, compatibilité descendante,
    - tables ORM (patients, clinical_cases, travel, symptoms, diagnoses,
      diagnostic_tests, medications, evidence_usage, sources, models,
      inferences, audit_events_orm) — vues relationnelles normalisées,
    - migrations versionnées : voir migrations/versions/.
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from tropirag.core.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    patient_json TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    urgency TEXT, severity TEXT,
    differentials_json TEXT,
    matched_rules_json TEXT,
    ai_layer TEXT,
    refusal TEXT
);
CREATE TABLE IF NOT EXISTS evidence_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT, unit_id TEXT NOT NULL,
    score REAL, used_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    audit_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    event TEXT NOT NULL,
    payload_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_analyses_case ON analyses(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_events(ts);
"""


class Database:
    """SQLite thread-safe (WAL) — gestion centralisée."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA)
        from tropirag.persistence.models import create_orm_schema
        create_orm_schema(self._conn)
        self._conn.commit()

    @classmethod
    def instance(cls, path: Path | None = None) -> "Database":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(path)
            return cls._instance

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
            return cur

    def query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    # --- transactions (Unit of Work) -----------------------------------------
    def begin(self) -> None:
        """Ouvre une transaction explicite (deferred)."""
        with self._lock:
            if not self._conn.in_transaction:
                self._conn.execute("BEGIN")

    def commit(self) -> None:
        with self._lock:
            self._conn.commit()

    def rollback(self) -> None:
        with self._lock:
            if self._conn.in_transaction:
                self._conn.rollback()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def tables(self) -> list[str]:
        rows = self.query("SELECT name FROM sqlite_master WHERE type='table' "
                          "AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [r["name"] for r in rows]

    def close(self) -> None:
        with self._lock:
            self._conn.close()


def reset_for_tests(path: Path) -> "Database":
    """Base jetable pour les tests."""
    if Path(path).exists():
        Path(path).unlink()
    return Database(path)
