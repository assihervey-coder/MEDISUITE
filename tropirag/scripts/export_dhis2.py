#!/usr/bin/env python3
"""TropiRAG — export DHIS2 des indicateurs de surveillance (V1.2, MSP-CI).

Usage :
    python scripts/export_dhis2.py                       # semaine en cours, dry-run
    python scripts/export_dhis2.py --period 2026W37      # semaine précise
    python scripts/export_dhis2.py --enqueue             # mettre en file offline
    python scripts/export_dhis2.py --status              # état de la file
    python scripts/export_dhis2.py --push                # envoyer la file (si serveur configuré)
    python scripts/export_dhis2.py --format adx          # rendu ADX 2.0 XML
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.datetime import local_now  # noqa: E402
from tropirag.integrations.dhis2.exporter import FORMATS, Dhis2Exporter  # noqa: E402
from tropirag.integrations.dhis2.mapper import (  # noqa: E402
    period_bounds,
    period_from_date,
)
from tropirag.integrations.dhis2.models import DataValueSet  # noqa: E402
from tropirag.integrations.dhis2.settings import load_dhis2_config  # noqa: E402


def _rows_for_period(repo, period: str) -> list[dict]:
    bounds = period_bounds(period)
    if bounds is None:
        print(f"Période invalide : {period} (format attendu : YYYYWww, ex. 2026W37)")
        sys.exit(2)
    return repo.analyses_between(bounds[0].isoformat(), bounds[1].isoformat())


def main() -> int:
    ap = argparse.ArgumentParser(description="Export DHIS2 — indicateurs TropiRAG")
    ap.add_argument("--period", default=None, help="YYYYWww (défaut : semaine en cours)")
    ap.add_argument("--org-unit", default=None, help="forcer l'organisation DHIS2")
    ap.add_argument("--format", choices=FORMATS, default="json")
    ap.add_argument("--enqueue", action="store_true",
                    help="mettre le payload en file offline (aucun envoi réseau)")
    ap.add_argument("--push", action="store_true",
                    help="tenter l'envoi de la file (requiert serveur configuré)")
    ap.add_argument("--status", action="store_true", help="état de la file offline")
    ap.add_argument("--no-payload", action="store_true", help="cacher le payload rendu")
    args = ap.parse_args()

    cfg = load_dhis2_config()
    exporter = Dhis2Exporter(cfg)

    if args.status:
        print(json.dumps(exporter.queue.status_summary(), ensure_ascii=False, indent=2))
        return 0

    if args.push:
        reports = exporter.flush_queue()
        if not reports:
            print("Aucun payload en attente.")
            return 0
        ok = sum(1 for r in reports if r.ok)
        for r in reports:
            state = "ENVOYÉ" if r.ok else "ÉCHEC"
            print(f"  [{state}] {r.status_code or ''} {r.detail[:120]}")
        print(f"\n{ok}/{len(reports)} payload(s) envoyé(s).")
        return 0 if ok == len(reports) else 1

    if args.org_unit:
        cfg.org_unit = args.org_unit

    period = args.period or period_from_date(local_now().date())

    from tropirag.persistence.repositories.case_repository import CaseRepository
    from tropirag.persistence.database import Database

    repo = CaseRepository(Database.instance())
    rows = _rows_for_period(repo, period)

    result = exporter.export(rows, period, enqueue=True if args.enqueue else False)

    print(f"Période            : {period}")
    print(f"Organisation (UID) : {cfg.org_unit}")
    print(f"Analyses couvertes : {len(rows)}")
    print("\nIndicateurs comptés :")
    for key, n in sorted(result.counts.items()):
        if n:
            print(f"  {key:24s} = {n}")

    if result.data_values:
        dvs = DataValueSet(data_values=result.data_values,
                           org_unit=cfg.org_unit, period=period)
        rendered = exporter.render(dvs, args.format)
        if not args.no_payload:
            print(f"\n--- payload {args.format.upper()} ---")
            print(rendered)
    else:
        print("\nAucune valeur à exporter pour cette période.")

    if result.enqueued:
        print("[file offline] payload enregistré — envoi différé jusqu'à configuration "
              "du serveur MSP-CI (voir docs/operations/DHIS2_EXPORT.md)")
    for note in result.notes:
        print(f"[note] {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
