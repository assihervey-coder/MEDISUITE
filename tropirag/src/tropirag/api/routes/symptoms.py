"""Routes symptômes : normalisation + taxonomie."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from tropirag.domain.symptoms.normalization import normalize_symptoms
from tropirag.domain.symptoms.taxonomy import SYMPTOMS

router = APIRouter()


class SymptomText(BaseModel):
    text: str


@router.post("/symptoms/normalize")
async def normalize(req: SymptomText) -> dict:
    syms = normalize_symptoms(req.text)
    return {"symptoms": [{"code": s.code, "label": s.label_fr,
                          "severity": s.severity} for s in syms]}


@router.get("/symptoms/taxonomy")
async def taxonomy() -> dict:
    return {"symptoms": [{"code": k, "fr": v["fr"], "en": v["en"]}
                         for k, v in sorted(SYMPTOMS.items())]}
