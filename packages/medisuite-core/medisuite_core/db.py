"""Base de données : SQLAlchemy 2.0, SQLite zéro-config en dev, PostgreSQL en prod.

Chaque microservice possède SON schéma (database-per-service) : la convention
est `sqlite:///data/<service>.db` en dev, `postgresql://...` en production.
"""
from __future__ import annotations

import os
import pathlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

ROOT = pathlib.Path(__file__).resolve().parents[3]


class Base(DeclarativeBase):
    pass


def new_id() -> str:
    """Identifiant court, préfixable, sans tiret (8+4+4 hex)."""
    return uuid.uuid4().hex[:16]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def engine_for(service_name: str, url: str | None = None) -> Engine:
    """Moteur SQLAlchemy pour un service donné (SQLite par défaut)."""
    if url is None:
        data_dir = ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        url = f"sqlite:///{data_dir / service_name}.db"
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, future=True)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _fk_on(dbapi_conn, _record):  # pragma: no cover
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.close()
    return engine


def init_db(engine: Engine, *models_meta) -> sessionmaker:
    """Crée les tables et retourne une fabrique de sessions."""
    for meta in models_meta:
        meta.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def with_session(SessionLocal) -> Session:
    """Contexte de session pratique pour les tests et scripts."""
    return SessionLocal()
