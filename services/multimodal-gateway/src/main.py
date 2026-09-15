from __future__ import annotations

import pathlib
import sys
from typing import Annotated

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from medisuite_core import security
from medisuite_core import auth_deps
from medisuite_core.http import create_service_app

app: FastAPI = create_service_app(
    "multimodal-gateway", "Passerelle Fusion Multimodale", "Orchestration des inférences fusion multi-modalités (ADR-0016/0017/0018) : collecte, qualité, inférence, explicabilité.", module_label="Passerelle Fusion Multimodale")

JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


MODALITES = {
    "imaging_2d": {"encodeur": "CNN 2D", "exemples": ["fond d'œil", "dermoscopie"]},
    "imaging_3d": {"encodeur": "CNN 3D / MONAI", "exemples": ["IRM", "scanner"]},
    "signal_1d": {"encodeur": "CNN 1D", "exemples": ["ECG 12 dérivations"]},
    "tabulaire": {"encodeur": "MLP", "exemples": ["biologie, démographie"]},
    "texte": {"encodeur": "transformer léger", "exemples": ["comptes-rendus"]},
    "genomique": {"encodeur": "embedding k-mers", "exemples": ["variantes"]},
    "waveform": {"encodeur": "CNN 1D", "exemples": ["CTG", "EEG"]},
}


@app.get("/api/v1/modalities", tags=["registre"])
def modalities() -> dict:
    return {"modalites": MODALITES,
            "politique_modalites_manquantes": "inférence dégradée élégante (ADR-0018)"}


@app.post("/api/v1/inference", tags=["inférence"])
def inference(payload: dict, user: dict = Depends(current_user)) -> dict:
    """Orchestration complète : collecte des encodages par modalité, contrôle de
    qualité, fusion cross-attention, retour + importance des modalités.

    Body : {"patient_id": ..., "task": "classification",
            "modalities": {"tabulaire": {"features": [...]},
                            "imaging_2d": {"tensor": [[...]]}, ...}}
    """
    modalities = payload.get("modalities", {})
    if not modalities:
        raise HTTPException(422, "aucune modalité fournie")
    try:
        sys.path.insert(0, str(ROOT / "ai"))
        from multimodal.core.fusion_engine import FusionEngine
        from multimodal.core.registry import ModalityRegistry
    except ImportError as exc:
        raise HTTPException(503, f"moteur de fusion indisponible : {exc}")

    engine = FusionEngine(ModalityRegistry.default_dimensions())
    result = engine.infer(modalities, task=payload.get("task", "classification"))
    result["patient_id"] = payload.get("patient_id", "")
    result["consentement_ia_verifie"] = bool(payload.get("consent_ia", False))
    return result
