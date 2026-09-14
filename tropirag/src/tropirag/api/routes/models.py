"""Route registre de modèles du mesh."""
from __future__ import annotations

from fastapi import APIRouter

from tropirag.ai.registry.model_registry import get_registry
from tropirag.ai.routing.model_router import ModelRouter
from tropirag.core.enums import ClinicalTask

router = APIRouter()


@router.get("/models")
async def list_models() -> dict:
    reg = get_registry()
    return {
        "models": reg.to_dict(),
        "invariants_violations": reg.validate_invariants(),
        "fingerprint": reg.fingerprint(),
    }


@router.get("/models/route")
async def route_demo(task: str, language: str = "fr") -> dict:
    from tropirag.core.config import get_config

    router_ = ModelRouter(get_registry(), inference_mode=get_config().inference.mode)
    decision = router_.route(ClinicalTask(task), language=language)
    return decision.to_dict()
