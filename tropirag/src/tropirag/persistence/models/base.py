"""Base ORM — mini-framework déclaratif sur SQLite (stdlib pure, zéro dépendance).

Objectif : 12 tables normalisées miroirs des entités du domaine, sans ORM tiers
(SQLAlchemy interdit en mode offline dur). Chaque modèle déclare :

    - ``TABLE``      : nom SQL,
    - ``COLUMNS``    : colonnes typées + contraintes,
    - ``DDL``        : ordre CREATE TABLE IF NOT EXISTS,
    - ``row_from_*`` : mappage domaine → ligne,
    - ``to_domain``  : ligne → domaine.

Les mappages sont auditables : le JSON intégral du payload reste stocké dans
``clinical_cases.payload_json`` (copie immuable), les tables normalisées sont
des vues relationnelles construites par-dessus — jamais l'inverse.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Column:
    """Déclaration de colonne typée."""

    name: str
    sql_type: str = "TEXT"            # TEXT | INTEGER | REAL | BLOB
    primary_key: bool = False
    nullable: bool = True
    default: str | None = None
    index: bool = False               # index b-tree à créer
    unique: bool = False

    def ddl(self) -> str:
        parts = [self.name, self.sql_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        elif not self.nullable:
            parts.append("NOT NULL")
        if self.unique:
            parts.append("UNIQUE")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)


def build_ddl(table: str, columns: list[Column], extra: str = "") -> str:
    """CREATE TABLE IF NOT EXISTS idempotent."""
    cols = ",\n    ".join(c.ddl() for c in columns)
    tail = f",\n    {extra}" if extra else ""
    return f"CREATE TABLE IF NOT EXISTS {table} (\n    {cols}{tail}\n)"


def index_ddl(table: str, columns: list[Column]) -> list[str]:
    return [f"CREATE INDEX IF NOT EXISTS idx_{table}_{c.name} ON {table}({c.name})"
            for c in columns if c.index and not c.primary_key]


class TableGateway:
    """Accès typé à une table : insert/upsert/count/select."""

    table: str = ""
    columns: list[Column] = []

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    # ------------------------------------------------------------------
    def ensure(self) -> None:
        self.conn.execute(build_ddl(self.table, self.columns))
        for stmt in index_ddl(self.table, self.columns):
            self.conn.execute(stmt)

    def insert(self, row: dict) -> None:
        keys = [c.name for c in self.columns if c.name in row]
        if not keys:
            return
        sql = (f"INSERT OR REPLACE INTO {self.table} ({', '.join(keys)}) "
               f"VALUES ({', '.join('?' * len(keys))})")
        self.conn.execute(sql, tuple(row[k] for k in keys))

    def insert_many(self, rows: list[dict]) -> int:
        n = 0
        for row in rows:
            self.insert(row)
            n += 1
        return n

    def select(self, where: str = "", params: tuple = (),
               order: str = "", limit: int = 0) -> list[sqlite3.Row]:
        sql = f"SELECT * FROM {self.table}"
        if where:
            sql += f" WHERE {where}"
        if order:
            sql += f" ORDER BY {order}"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return self.conn.execute(sql, params).fetchall()

    def count(self, where: str = "", params: tuple = ()) -> int:
        sql = f"SELECT COUNT(*) AS n FROM {self.table}"
        if where:
            sql += f" WHERE {where}"
        row = self.conn.execute(sql, params).fetchone()
        return int(row["n"]) if row else 0
