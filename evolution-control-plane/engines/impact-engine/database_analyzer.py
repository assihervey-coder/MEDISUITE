"""Analyseur base de données — migrations et schémas touchés."""
from __future__ import annotations

DB_OWNERS = {
    "patient-service", "auth-service", "laboratory-service",
    "imaging-service", "ecrf-service",
}


def analyze_databases(changed_paths: list[str]) -> dict:
    migrations = [p for p in changed_paths if p.startswith("migrations/")]
    owners = [c for c in changed_paths
              if c.split("/")[0:2] == ["services"] and c.split("/")[1] in DB_OWNERS]
    return {
        "databases": 1 if (migrations or owners) else 0,
        "migration_files": migrations,
        "owning_services": sorted({p.split("/")[1] for p in owners}),
    }
