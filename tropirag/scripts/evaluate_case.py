#!/usr/bin/env python3
"""Évalue un cas : exécute le pipeline et imprime un rapport complet."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tropirag.core.datetime import local_now  # noqa: E402
from tropirag.response_engine.response_orchestrator import process_case  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="payload du cas")
    ap.add_argument("--out", help="sauvegarder la réponse en JSON")
    args = ap.parse_args()
    r = process_case(json.loads(args.json))
    if args.out:
        Path(args.out).write_text(json.dumps(r.to_dict(), ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        print(f"réponse → {args.out}")
    print(json.dumps({k: v for k, v in r.to_dict().items() if k != "narrative"},
                     ensure_ascii=False, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
