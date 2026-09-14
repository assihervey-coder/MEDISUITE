"""Dépôt des modèles — état runtime (legacy) + snapshot ORM du registry."""
from __future__ import annotations

import json
import time

from tropirag.persistence.database import Database


class ModelRepository:

    def __init__(self, db: Database) -> None:
        self.db = db
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS models (model_id TEXT PRIMARY KEY,"
            " state TEXT, version TEXT, updated_at TEXT)")

    # --- état runtime (legacy, suivi up/down) ------------------------------
    def upsert(self, model_id: str, state: str, version: str = "latest") -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO models (model_id, state, version, updated_at) VALUES (?,?,?,?)",
            (model_id, state, version, time.strftime("%Y-%m-%dT%H:%M:%S")))

    def all_states(self) -> list[dict]:
        rows = self.db.query("SELECT * FROM models ORDER BY model_id")
        return [dict(r) for r in rows]

    # --- snapshot ORM du registry -----------------------------------------
    def sync_registry(self, registry) -> int:
        """Snapshot le ModelRegistry complet dans models_registry (ORM)."""
        from tropirag.persistence.models.model import row_from_model_meta
        conn = self.db.connection
        conn.execute("DELETE FROM models_registry")
        n = 0
        for m in registry.all():
            row = row_from_model_meta(m)
            keys = list(row)
            conn.execute(
                f"INSERT OR REPLACE INTO models_registry ({', '.join(keys)}) "
                f"VALUES ({', '.join('?' * len(keys))})",
                tuple(row[k] for k in keys))
            n += 1
        self.db.commit()
        return n

    def registry_rows(self) -> list[dict]:
        rows = self.db.query("SELECT * FROM models_registry ORDER BY priority DESC")
        out = []
        for r in rows:
            out.append({
                "model_id": r["model_id"], "display_name": r["display_name"],
                "family": r["family"], "gateway": r["gateway"],
                "vram_gb": r["vram_gb"], "priority": r["priority"],
                "clinically_validated": bool(r["clinically_validated"]),
                "capabilities": json.loads(r["capabilities_json"] or "{}"),
                "health": r["health"],
            })
        return out

    def by_family(self, family: str) -> list[dict]:
        return [m for m in self.registry_rows() if m["family"] == family]
