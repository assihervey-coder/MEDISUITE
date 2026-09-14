"""Route analyse clinique (pipeline complet)."""
from __future__ import annotations

from fastapi import APIRouter

from tropirag.api.schemas.clinical_case import CaseRequest
from tropirag.response_engine.response_orchestrator import ResponseOrchestrator

router = APIRouter()

_orch: ResponseOrchestrator | None = None


def get_orchestrator() -> ResponseOrchestrator:
    global _orch
    if _orch is None:
        _orch = ResponseOrchestrator()
    return _orch


@router.post("/clinical/analyze")
async def analyze_case(req: CaseRequest) -> dict:
    payload = req.model_dump(exclude={"use_ai", "language"}, exclude_none=True)
    r = get_orchestrator().process(payload, language=req.language, use_ai=req.use_ai)
    return r.to_dict()
