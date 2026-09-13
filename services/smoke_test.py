#!/usr/bin/env python3
"""Smoke test : vérifie /health sur chaque service démarré (concurrence asynchrone)."""
import asyncio
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.registry import ALL_SERVICES  # noqa: E402


async def check(client: httpx.AsyncClient, svc: dict) -> tuple[str, bool, str]:
    try:
        r = await client.get(f"http://localhost:{svc['port']}/health", timeout=3)
        return svc["name"], r.status_code == 200, r.json().get("version", "")
    except Exception:
        return svc["name"], False, ""


async def main() -> int:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(check(client, s) for s in ALL_SERVICES))
    ok = sum(1 for _, up, _ in results if up)
    for name, up, version in results:
        print(f"  {'✅' if up else '❌'} {name:<28} {version}")
    print(f"\n{ok}/{len(results)} services en bonne santé.")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
