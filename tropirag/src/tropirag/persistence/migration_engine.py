"""Moteur de migrations — versionnage déterministe du schéma SQLite.

Format compatible-esprit Alembic mais SANS dépendance : chaque fichier de
``migrations/versions/`` expose ``upgrade(conn)`` / ``downgrade(conn)`` et un
``REVISION`` + ``DOWN_REVISION`` chaînés. L'état est suivi dans la table
``schema_migrations`` (version, applied_at).

Cycle :
    pending() → upgrade(conn) → record version
    rollback → downgrade(conn) → version précédente
"""
from __future__ import annotations

import importlib.util
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
)
"""


@dataclass(slots=True)
class Migration:
    revision: str
    down_revision: str | None
    module: object
    path: Path

    @property
    def label(self) -> str:
        return self.path.stem


def discover(versions_dir: Path) -> list[Migration]:
    """Charge les migrations triées par chaîne DOWN_REVISION."""
    out: list[Migration] = []
    for f in sorted(versions_dir.glob("*.py")):
        if f.name.startswith("__"):
            continue
        spec = importlib.util.spec_from_file_location(f"tropirag_migration_{f.stem}", f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            continue
        rev = getattr(mod, "REVISION", None)
        if rev is None:
            continue
        out.append(Migration(revision=rev,
                             down_revision=getattr(mod, "DOWN_REVISION", None),
                             module=mod, path=f))
    return _order(out)


def _order(migrations: list[Migration]) -> list[Migration]:
    """Tri topologique de la chaîne down_revision."""
    by_rev = {m.revision: m for m in migrations}
    roots = [m for m in migrations if m.down_revision is None]
    if len(roots) != 1:
        raise ValueError(f"chaîne de migrations invalide : {len(roots)} racine(s)")
    ordered: list[Migration] = []
    current = roots[0]
    ordered.append(current)
    while True:
        children = [m for m in migrations
                    if m.down_revision == current.revision and m.revision != current.revision]
        if not children:
            break
        if len(children) > 1:
            raise ValueError(f"embranchement interdit après {current.revision}")
        current = children[0]
        ordered.append(current)
    if len(ordered) != len(migrations):
        missing = [m.revision for m in migrations if m not in ordered]
        raise ValueError(f"migrations hors chaîne : {missing}")
    return ordered


class MigrationEngine:
    """Applique / annule les migrations sur une connexion SQLite."""

    def __init__(self, conn: sqlite3.Connection, versions_dir: Path) -> None:
        self.conn = conn
        self.versions_dir = Path(versions_dir)
        self.conn.executescript(MIGRATIONS_TABLE)
        self.conn.commit()

    # ------------------------------------------------------------------
    def applied(self) -> list[str]:
        """Versions appliquées, DANS L'ORDRE DE LA CHAÎNE (déterministe)."""
        rows = self.conn.execute(
            "SELECT version FROM schema_migrations").fetchall()
        done = {r["version"] for r in rows}
        return [m.revision for m in discover(self.versions_dir) if m.revision in done]

    def pending(self) -> list[Migration]:
        done = set(self.applied())
        return [m for m in discover(self.versions_dir) if m.revision not in done]

    def current(self) -> str | None:
        applied = self.applied()
        return applied[-1] if applied else None

    # ------------------------------------------------------------------
    def upgrade(self, target: str | None = None) -> list[str]:
        """Applique les migrations en attente (jusqu'à target, sinon tête)."""
        chain = discover(self.versions_dir)
        if target and target not in {m.revision for m in chain}:
            raise ValueError(f"révision cible inconnue : {target}")
        done = set(self.applied())
        applied_now: list[str] = []
        for m in chain:
            if m.revision in done:
                continue
            try:
                # NOTE : executescript() (DDL) commite implicitement en sqlite3 —
                # les migrations sont donc idempotentes (IF NOT EXISTS) et
                # reproductibles en cas de reprise après échec mi-chemin.
                m.module.upgrade(self.conn)
                self.conn.execute(
                    "INSERT OR REPLACE INTO schema_migrations (version, applied_at) "
                    "VALUES (?, ?)", (m.revision, time.strftime("%Y-%m-%dT%H:%M:%S")))
                self.conn.commit()
                applied_now.append(m.revision)
            except Exception:
                self.conn.rollback()
                raise
            if target and m.revision == target:
                break
        return applied_now

    def downgrade(self, steps: int = 1) -> list[str]:
        """Annule les N dernières migrations."""
        chain = discover(self.versions_dir)
        applied = self.applied()
        undone: list[str] = []
        by_rev = {m.revision: m for m in chain}
        for _ in range(max(0, steps)):
            if not applied:
                break
            rev = applied.pop()
            m = by_rev.get(rev)
            if m is None:
                raise ValueError(f"migration appliquée introuvable : {rev}")
            m.module.downgrade(self.conn)
            self.conn.execute("DELETE FROM schema_migrations WHERE version = ?", (rev,))
            self.conn.commit()
            undone.append(rev)
        return undone

    def stamp(self, revision: str) -> None:
        """Marque une version comme appliquée sans l'exécuter (reprise d'urgence).

        Sémantique Alembic : marquer `revision` marque aussi tout son préfixe
        de chaîne (les migrations antérieures sont considérées appliquées).
        """
        chain = discover(self.versions_dir)
        revs = [m.revision for m in chain]
        if revision not in revs:
            raise ValueError(f"révision inconnue : {revision}")
        prefix = revs[: revs.index(revision) + 1]
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        for rev in prefix:
            self.conn.execute(
                "INSERT OR REPLACE INTO schema_migrations (version, applied_at) "
                "VALUES (?, ?)", (rev, now))
        self.conn.commit()

    def history(self) -> list[dict]:
        chain = discover(self.versions_dir)
        done = set(self.applied())
        return [{"revision": m.revision, "label": m.label,
                 "applied": m.revision in done,
                 "doc": (getattr(m.module, "__doc__", "") or "").strip().splitlines()[0]
                 if getattr(m.module, "__doc__", None) else ""}
                for m in chain]
