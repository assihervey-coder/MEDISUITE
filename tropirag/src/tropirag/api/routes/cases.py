"""Routes de gestion des cas."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from tropirag.api.routes.clinical import get_orchestrator
from tropirag.api.schemas.clinical_case import CaseRequest
from tropirag.persistence.database import Database

router = APIRouter()

_db: Database | None = None


def _db_instance() -> Database:
    global _db
    if _db is None:
        _db = Database.instance()
    return _db


@router.post("/cases")
async def create_and_analyze(req: CaseRequest) -> dict:
    payload = req.model_dump(exclude={"use_ai", "language"}, exclude_none=True)
    orch = get_orchestrator()
    r = orch.process(payload, language=req.language, use_ai=req.use_ai)
    db = _db_instance()
    from tropirag.persistence.repositories.case_repository import CaseRepository

    repo = CaseRepository(db)
    repo.save_case(r.case_id, payload.get("patient") or {}, payload)
    repo.save_analysis(r.case_id, r.urgency, r.severity, r.differentials,
                       r.matched_rule_ids, r.ai_layer, r.refusal)
    return r.to_dict()


@router.get("/cases")
async def list_cases(limit: int = 20) -> dict:
    from tropirag.persistence.repositories.case_repository import CaseRepository

    repo = CaseRepository(_db_instance())
    return {"analyses": repo.recent_analyses(limit), "stats": repo.stats()}


@router.get("/cases/{case_id}")
async def get_case(case_id: str) -> dict:
    from tropirag.persistence.repositories.case_repository import CaseRepository

    repo = CaseRepository(_db_instance())
    case = repo.get_case(case_id)
    if case is None:
        raise HTTPException(404, f"cas {case_id} introuvable")
    return case
