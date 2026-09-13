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
from medisuite_core.http import create_service_app

app: FastAPI = create_service_app(
    "explainability-service", "Explicabilité IA", "Importance des modalités, visualisation d'attention, heatmaps GradCAM-lite (ADR-0015).", module_label="Explicabilité IA")

JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


import numpy as np
from pydantic import BaseModel as BModel


class AttentionIn(BModel):
    attention: dict[str, float]  # modalité → poids brut


class GridIn(BModel):
    grid: list[list[float]]      # carte brute (ex. activation de couche)


@app.post("/api/v1/modality-importance", tags=["explicabilité"])
def modality_importance(body: AttentionIn) -> dict:
    """Normalise les poids d'attention en pourcentages par modalité."""
    total = sum(max(0.0, v) for v in body.attention.values())
    if total <= 0:
        raise HTTPException(422, "poids d'attention tous nuls ou négatifs")
    parts = {k: round(100 * max(0.0, v) / total, 1)
             for k, v in body.attention.items()}
    top = max(parts, key=parts.get)
    return {"importance_pct": parts, "modalite_dominante": top,
            "lecture": (f"la décision repose surtout sur « {top} » "
                        f"({parts[top]} % des poids d'attention)")}


@app.post("/api/v1/attention-viz", tags=["explicabilité"])
def attention_viz(body: AttentionIn) -> dict:
    total = sum(max(0.0, v) for v in body.attention.values()) or 1.0
    vals = np.array([max(0.0, v) / total for v in body.attention.values()])
    return {"labels": list(body.attention.keys()),
            "valeurs": [round(float(v), 4) for v in vals],
            "ordre": sorted(body.attention.keys(),
                            key=lambda k: -body.attention[k])}


@app.post("/api/v1/gradcam-lite", tags=["explicabilité"])
def gradcam_lite(body: GridIn) -> dict:
    """Normalise une carte d'activation en heatmap [0,1] + centroïde de saillance."""
    arr = np.array(body.grid, dtype=float)
    if arr.size == 0 or arr.max() == arr.min():
        raise HTTPException(422, "grille vide ou constante")
    norm = (arr - arr.min()) / (arr.max() - arr.min())
    idx = np.unravel_index(np.argmax(norm), norm.shape)
    ys, xs = np.mgrid[0:norm.shape[0], 0:norm.shape[1]]
    cy = float((norm * ys).sum() / norm.sum())
    cx = float((norm * xs).sum() / norm.sum())
    return {"heatmap": [[round(float(v), 3) for v in row] for row in norm],
            "pic": {"ligne": int(idx[0]), "colonne": int(idx[1])},
            "centroid_saliency": {"y": round(cy, 2), "x": round(cx, 2)}}
