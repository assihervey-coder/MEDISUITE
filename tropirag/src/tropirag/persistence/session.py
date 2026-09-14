"""Gestion de session persistance (V1 : contexte simple)."""
from __future__ import annotations

from contextlib import contextmanager

from tropirag.persistence.database import Database


@contextmanager
def session(db: Database | None = None):
    """Contexte transactionnel léger."""
    from tropirag.persistence.database import Database as _DB

    database = db or _DB.instance()
    try:
        yield database
    finally:
        pass  # SQLite : commit implicite dans execute()
