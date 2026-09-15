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
    "hl7-gateway", "Passerelle HL7", "Hub MLLP : réception, ACK automatique, routage par type de message.", module_label="Passerelle HL7")

JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


from medisuite_core import hl7

_queue_stats: dict[str, int] = {}

ROUTES = {"ADT": "http://localhost:8002 (patient-service)",
          "ORM": "http://localhost:8004 (laboratory-service)",
          "ORU": "http://localhost:8004 (laboratory-service)",
          "SIU": "module obstetrics / rendez-vous"}


@app.get("/api/v1/routes", tags=["routage"])
def routes() -> dict:
    return {"routes": ROUTES,
            "mlp_listen": "0.0.0.0:2575 (Mirth/analyteurs — v0.2 socket natif)"}


@app.post("/api/v1/process", tags=["traitement"])
def process(payload: dict) -> dict:
    """Reçoit tout message HL7 v2 : parse, ACK, routage selon MSH-9."""
    msg = hl7.parse(payload.get("message", ""))
    mtype = msg.message_type
    if not mtype:
        raise HTTPException(422, "MSH absent ou type vide")
    family = mtype.split("^")[0]
    _queue_stats[family] = _queue_stats.get(family, 0) + 1
    return {"type": mtype,
            "control_id": msg.field("MSH", 9),
            "ack": hl7.ack_for(msg),
            "destination": ROUTES.get(family, "file morte (DLQ)")}


@app.post("/api/v1/queue/push", tags=["file"])
def queue_push(payload: dict) -> dict:
    family = payload.get("type", "ADT").split("^")[0]
    _queue_stats[family] = _queue_stats.get(family, 0) + 1
    return {"type": family, "en_file": _queue_stats[family]}


@app.get("/api/v1/queue/stats", tags=["file"])
def queue_stats() -> dict:
    return {"compteurs": _queue_stats, "retard_critique": None}
