#!/usr/bin/env python3
"""CLI de migrations — upgrade / downgrade / current / history / stamp.

Usage :
    python scripts/migrate.py current
    python scripts/migrate.py upgrade            # jusqu'à la tête
    python scripts/migrate.py upgrade 0002_clinical_analyses
    python scripts/migrate.py downgrade 1         # annule la dernière
    python scripts/migrate.py history
    python scripts/migrate.py stamp 0004_ai_mesh_audit
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))  # pour importer migrations/env.py

from tropirag.persistence.migration_engine import MigrationEngine  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Migrations TropiRAG (stdlib pure)")
    ap.add_argument("command", choices=["current", "upgrade", "downgrade",
                                         "history", "stamp"])
    ap.add_argument("value", nargs="?", help="cible (upgrade/stamp) ou pas (downgrade)")
    args = ap.parse_args()

    import migrations.env as env  # noqa: E402

    errors = env.validate()
    if errors:
        for e in errors:
            print(f"✗ {e}")
        return 1

    conn = env.connect()
    engine = MigrationEngine(conn, env.VERSIONS_DIR)

    try:
        if args.command == "current":
            print(engine.current() or "(aucune migration appliquée)")

        elif args.command == "upgrade":
            target = args.value
            applied = engine.upgrade(target)
            if applied:
                for rev in applied:
                    print(f"✓ appliquée : {rev}")
                print(f"Tête courante : {engine.current()}")
            else:
                print("Rien à appliquer — schéma déjà à jour.")

        elif args.command == "downgrade":
            steps = int(args.value or 1)
            undone = engine.downgrade(steps)
            for rev in undone:
                print(f"↩ annulée : {rev}")
            print(f"Tête courante : {engine.current()}")

        elif args.command == "history":
            for row in engine.history():
                mark = "✓" if row["applied"] else " "
                print(f"[{mark}] {row['revision']:28s} {row['label']:32s} {row['doc']}")

        elif args.command == "stamp":
            if not args.value:
                print("✗ révision requise pour stamp")
                return 1
            engine.stamp(args.value)
            print(f"⇩ marquée : {args.value}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
