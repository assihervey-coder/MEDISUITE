"""Routes de surveillance — cartographie des éclosions (V1.3).

    GET /api/v1/surveillance/map?days=30&district=abidjan
        clusters par district sanitaire CI + signaux d'éclosion
    GET /api/v1/surveillance/districts
        métadonnées des 14 districts (libellés, grille cartographique)

Les comptes dérivent exclusivement des analyses déterministes persistées —
aucune IA ne participe au comptage (même source de vérité que l'export DHIS2).
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from tropirag.integrations.surveillance import CI_DISTRICTS, OutbreakMonitor
from tropirag.persistence.database import Database

router = APIRouter()

_monitor: OutbreakMonitor | None = None


def get_monitor() -> OutbreakMonitor:
    global _monitor
    if _monitor is None:
        _monitor = OutbreakMonitor(Database.instance())
    return _monitor


@router.get("/surveillance/map")
async def surveillance_map(
    days: int = Query(default=30, ge=1, le=365),
    district: str | None = Query(default=None,
                                 description="filtrer un district (clé, ex. abidjan)"),
) -> dict:
    snapshot = get_monitor().clusters(days=days)
    if district:
        keys = {d.key for d in CI_DISTRICTS.values()}
        if district not in keys:
            from fastapi import HTTPException

            raise HTTPException(404, f"district inconnu : {district} "
                                      f"(attendus : {sorted(keys)})")
        snapshot["districts"] = [d for d in snapshot["districts"]
                                if d["key"] == district]
    return snapshot


@router.get("/surveillance/districts")
async def surveillance_districts() -> dict:
    return {"districts": [
        {"key": d.key, "label": d.label, "chief_town": d.chief_town,
         "grid": list(d.grid)} for d in CI_DISTRICTS.values()
    ]}
