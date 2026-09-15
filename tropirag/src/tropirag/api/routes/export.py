"""Routes d'export DHIS2 — V1.2, MSP-CI.

    POST /api/v1/export/dhis2         export de la période (file offline par défaut)
    GET  /api/v1/export/dhis2/status  état de la file d'attente
    POST /api/v1/export/dhis2/push    tentative d'envoi de la file (explicite)
    GET  /api/v1/export/dhis2/cron    état du cron hebdo (config, dernier envoi)
    POST /api/v1/export/dhis2/cron/run  déclenchement manuel d'un cycle
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from tropirag.core.datetime import local_now
from tropirag.integrations.dhis2.exporter import Dhis2Exporter, FORMATS
from tropirag.integrations.dhis2.mapper import period_bounds, period_from_date
from tropirag.integrations.dhis2.settings import load_dhis2_config
from tropirag.persistence.database import Database

router = APIRouter()

_db: Database | None = None
_exporter: Dhis2Exporter | None = None


def _get_db() -> Database:
    global _db
    if _db is None:
        _db = Database.instance()
    return _db


def get_exporter() -> Dhis2Exporter:
    global _exporter
    if _exporter is None:
        _exporter = Dhis2Exporter(load_dhis2_config())
    return _exporter


class ExportRequest(BaseModel):
    period: str | None = Field(default=None, description="YYYYWww (défaut : semaine en cours)")
    org_unit: str | None = None
    format: str = "json"
    enqueue: bool | None = Field(
        default=None, description="True : forcer la file ; False : dry-run ; défaut : config")
    limit_rows: int = Field(default=10000, ge=1, le=100000)


@router.post("/export/dhis2")
async def export_dhis2(req: ExportRequest) -> dict:
    if req.format not in FORMATS:
        raise HTTPException(422, f"format inconnu : {req.format} (attendus : {FORMATS})")

    period = req.period or period_from_date(local_now().date())
    bounds = period_bounds(period)
    if bounds is None:
        raise HTTPException(422, "période invalide — format attendu : YYYYWww (ex. 2026W37)")

    from tropirag.persistence.repositories.case_repository import CaseRepository

    repo = CaseRepository(_get_db())
    rows = repo.analyses_between(bounds[0].isoformat(), bounds[1].isoformat())[:req.limit_rows]

    exp = get_exporter()
    if req.org_unit:
        exp.cfg.org_unit = req.org_unit
    result = exp.export(rows, period, enqueue=req.enqueue)

    # rendu du format demandé (payload humainement vérifiable avant envoi)
    from tropirag.integrations.dhis2.models import DataValueSet

    dvs = DataValueSet(data_values=result.data_values,
                       org_unit=exp.cfg.org_unit, period=period)
    payload_rendered = exp.render(dvs, req.format)

    return {
        "period": period,
        "org_unit": exp.cfg.org_unit,
        "rows_analyzed": len(rows),
        "counts": result.counts,
        "data_values": [dv.to_json() for dv in result.data_values],
        "format": req.format,
        "payload": payload_rendered,
        "enqueued": result.enqueued,
        "pushed": result.pushed,
        "notes": result.notes,
        "disclaimer": "Indicateurs agrégés dérivés des analyses déterministes TropiRAG — "
                      "UIDs à confirmer avec le dictionnaire de données DHIS2 du MSP-CI.",
    }


@router.get("/export/dhis2/status")
async def dhis2_status() -> dict:
    exp = get_exporter()
    summary = exp.queue.status_summary()
    return {
        "queue": summary,
        "config": {
            "mode": exp.cfg.mode,
            "org_unit": exp.cfg.org_unit,
            "transport_ready": exp.cfg.transport_ready,
            "elements_mapped": len(exp.cfg.data_elements),
        },
    }


@router.post("/export/dhis2/push")
async def dhis2_push() -> dict:
    exp = get_exporter()
    reports = exp.flush_queue()
    if not reports:
        return {"pushed": 0, "detail": "aucun payload en attente"}
    ok = sum(1 for r in reports if r.ok)
    return {
        "pushed": ok,
        "failed": len(reports) - ok,
        "details": [{"ok": r.ok, "status_code": r.status_code,
                     "detail": r.detail} for r in reports],
    }


# ---------------------------------------------------------------------------
# Cron hebdomadaire MSP-CI (V1.4) — export/push automatique de la semaine écoulée
# ---------------------------------------------------------------------------
@router.get("/export/dhis2/cron")
async def dhis2_cron_status() -> dict:
    from tropirag.integrations.dhis2.scheduler import status as cron_status

    return cron_status()


@router.post("/export/dhis2/cron/run")
async def dhis2_cron_run() -> dict:
    """Déclenchement manuel du même cycle que le cron (validation, démo,
    rattrapage) — n'altère pas le prochain créneau planifié."""
    from tropirag.core.datetime import local_now

    from tropirag.integrations.dhis2.scheduler import run_weekly_job, save_state, load_state

    report = run_weekly_job(local_now())
    state = load_state()
    state["last_manual_run"] = report
    save_state(state)
    return report
