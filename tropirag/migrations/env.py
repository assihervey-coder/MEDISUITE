"""Configuration de l'environnement de migrations TropiRAG.

Équivalent fonctionnel d'un alembic/env.py — stdlib pure :
    - résolution du chemin de base (surcharge TROPIRAG_DB_PATH),
    - répertoire des versions (migrations/versions/),
    - validation des chemins (échec explicite et précoce).

Utilisé par ``src/tropirag/persistence/migration_engine.py`` et
``scripts/migrate.py``.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# Racine du projet : migrations/../
MIGRATIONS_DIR = Path(__file__).resolve().parent
VERSIONS_DIR = MIGRATIONS_DIR / "versions"
PROJECT_ROOT = MIGRATIONS_DIR.parent

# Base de données cible (même règle que core.config)
DB_PATH = Path(
    os.environ.get("TROPIRAG_DB_PATH")
    or (PROJECT_ROOT / "db" / "tropirag.sqlite3")
)


def connect() -> sqlite3.Connection:
    """Connexion configurée (WAL, FK actives, rows dict-like)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def validate() -> list[str]:
    """Contrôles de santé de l'environnement — liste d'erreurs (vide = OK)."""
    errors: list[str] = []
    if not VERSIONS_DIR.exists():
        errors.append(f"répertoire des versions introuvable : {VERSIONS_DIR}")
    elif not any(VERSIONS_DIR.glob("*.py")):
        errors.append(f"aucune migration dans {VERSIONS_DIR}")
    return errors
