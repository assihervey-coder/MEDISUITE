"""${message}

Révision      : ${up_revision}
Révision base : ${down_revision --- None: repr}
Créée le      : ${create_date}

Usage :
    cp migrations/script.py.mako migrations/versions/<ordre>_<slug>.py
Puis remplir upgrade()/downgrade() — DDL idempotent obligatoire
(CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS).
"""
from __future__ import annotations

import sqlite3

REVISION = ${repr(up_revision)}
DOWN_REVISION = ${repr(down_revision)}


def upgrade(conn: sqlite3.Connection) -> None:
    ${passes if passes else "pass"}


def downgrade(conn: sqlite3.Connection) -> None:
    ${repr(downgrade) if downgrade else "pass"}
