"""Dépôt d'usage des preuves."""
from __future__ import annotations

import time

from tropirag.persistence.database import Database


class EvidenceRepository:

    def __init__(self, db: Database) -> None:
        self.db = db

    def record_usage(self, case_id: str, unit_scores: dict[str, float]) -> None:
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        for uid, score in unit_scores.items():
            self.db.execute(
                "INSERT INTO evidence_usage (case_id, unit_id, score, used_at) VALUES (?,?,?,?)",
                (case_id, uid, float(score), now))

    def top_used(self, limit: int = 10) -> list[dict]:
        rows = self.db.query(
            "SELECT unit_id, COUNT(*) AS uses, AVG(score) AS avg_score "
            "FROM evidence_usage GROUP BY unit_id ORDER BY uses DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]
