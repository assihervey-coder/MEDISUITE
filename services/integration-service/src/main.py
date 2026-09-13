from __future__ import annotations

import pathlib
import sys
from typing import Annotated

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import JSON, String, select
from sqlalchemy.orm import Mapped, mapped_column

from medisuite_core import security
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.events import bus
from medisuite_core.http import create_service_app
from medisuite_core.rbac import can

app: FastAPI = create_service_app(
    "integration-service", "Intégration HL7/FHIR", "Hub d'interopérabilité : HL7 v2.5 (4 flux + ACK + MLLP), FHIR R4, IHE.", module_label="Intégration HL7/FHIR")

engine = engine_for("integration-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError:
        return {"sub": "anon", "role": ""}


from medisuite_core import fhir as fhir_mod
from medisuite_core import hl7
from medisuite_core.seed import generate_patient
import random


class RouteLog(Base):
    __tablename__ = "route_log"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    message_type: Mapped[str] = mapped_column(String(20), index=True)
    control_id: Mapped[str] = mapped_column(String(30))
    destination: Mapped[str] = mapped_column(String(60))
    statut: Mapped[str] = mapped_column(String(20), default="routé")


SessionLocal = init_db(engine, Base.metadata)

ROUTES = {"ADT": "patient-service", "ORM": "laboratory-service / imaging-service",
          "ORU": "laboratory-service", "SIU": "appointment (module obstetrics)",
          "DFT": "billing (facturation)"}


@app.get("/api/v1/routes", tags=["routage"])
def routes() -> dict:
    return {"routes": ROUTES}


@app.post("/api/v1/hl7/parse", tags=["HL7 v2"])
def hl7_parse(payload: dict) -> dict:
    msg = hl7.parse(payload.get("message", ""))
    return {"type": msg.message_type,
            "control_id": msg.field("MSH", 9),
            "patient_id": msg.field("PID", 3),
            "patient_nom": msg.field("PID", 5, component=0),
            "segments": [s[0] for s in msg.segments]}


@app.post("/api/v1/hl7/build/adt", tags=["HL7 v2"])
def build_adt(patient: dict) -> dict:
    msg = hl7.build_adt_a08(patient)
    return {"message": msg, "mllp_hex": hl7.mllp_frame(msg).hex()}


@app.post("/api/v1/hl7/ack", tags=["HL7 v2"])
def make_ack(payload: dict) -> dict:
    msg = hl7.parse(payload.get("message", ""))
    return {"ack": hl7.ack_for(msg, ok=payload.get("ok", True))}


@app.post("/api/v1/mllp/frame", tags=["MLLP"])
def mllp_frame(payload: dict) -> dict:
    framed = hl7.mllp_frame(payload.get("message", ""))
    return {"hex": framed.hex(), "octets": len(framed)}


@app.post("/api/v1/mllp/unframe", tags=["MLLP"])
def mllp_unframe(payload: dict) -> dict:
    try:
        return {"message": hl7.mllp_unframe(bytes.fromhex(payload["hex"]))}
    except ValueError as exc:
        raise HTTPException(422, f"hex invalide : {exc}")


@app.get("/api/v1/fhir/patients", tags=["FHIR R4"])
def fhir_patients(n: int = 5) -> dict:
    rng = random.Random(7)
    bundle = fhir_mod.bundle(
        [fhir_mod.patient_to_fhir(p | {"id": f"seed{i}"})
         for i, p in enumerate(generate_patient(rng, n))])
    return bundle


@app.post("/api/v1/fhir/patient", tags=["FHIR R4"])
def fhir_patient(patient: dict) -> dict:
    return fhir_mod.patient_to_fhir(patient)


# ── Serveur FHIR central (HAPI JPA, v0.4) ─────────────────────────────────────
# Le hub relaie les opérations REST FHIR R4 vers le référentiel HAPI
# (MEDISUITE_FHIR_BASE). Écriture protégée par RBAC patient.write,
# lecture par patient.read — fail-closed via medisuite_core.rbac.

from medisuite_core import hapi_client as hapi_mod
from medisuite_core import rbac as rbac_mod

hapi = hapi_mod.HapiClient()


@app.get("/api/v1/fhir/server/status", tags=["FHIR serveur"])
def fhir_server_status(user: dict = Depends(current_user)) -> dict:
    """Statut du référentiel HAPI : version R4, joignabilité, base configurée."""
    if not rbac_mod.can(user["role"], "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    return {"reachable": hapi.ping(), "base": hapi.base,
            "fhir_version": "4.0.1" if hapi.ping() else None}


@app.get("/api/v1/fhir/server/metadata", tags=["FHIR serveur"])
def fhir_server_metadata(user: dict = Depends(current_user)) -> dict:
    """CapabilityStatement du serveur HAPI (ressources, opérations, recherche)."""
    if not rbac_mod.can(user["role"], "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    try:
        return hapi.capabilities()
    except hapi_mod.FhirError as exc:
        raise HTTPException(502, str(exc))


@app.get("/api/v1/fhir/server/patients", tags=["FHIR serveur"])
def fhir_server_search(family: str | None = None, identifier: str | None = None,
                       n: int = 20, user: dict = Depends(current_user)) -> dict:
    """Recherche Patient sur HAPI (Bundle searchset) — relais QIDO-like."""
    if not rbac_mod.can(user["role"], "patient.read"):
        raise HTTPException(403, "permission patient.read requise")
    try:
        return hapi.search_patients(family=family, identifier=identifier,
                                    count=max(1, min(n, 100)))
    except hapi_mod.FhirError as exc:
        raise HTTPException(502, str(exc))


@app.post("/api/v1/fhir/server/patients", tags=["FHIR serveur"], status_code=201)
def fhir_server_create(patient: dict,
                       user: dict = Depends(current_user)) -> dict:
    """Création d'un Patient FHIR R4 sur le référentiel central (RBAC patient.write)."""
    if not rbac_mod.can(user["role"], "patient.write"):
        raise HTTPException(403, "permission patient.write requise")
    resource = fhir_mod.patient_to_fhir(patient)
    try:
        created = hapi.create("Patient", resource)
    except hapi_mod.FhirError as exc:
        raise HTTPException(502, str(exc))
    bus.publish("fhir.patient.created",
                {"fhir_id": created["id"], "dossier": patient.get("numero_dossier", "")})
    return created
