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
    "dicom-gateway", "Passerelle DICOM", "Bordure DICOM : anonymisation, routage Orthanc, C-FIND worklist léger.", module_label="Passerelle DICOM")

JWT_SECRET = "medisuite-dev-secret-change-in-prod"


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict:
    """Identité : absent → anon ; jeton invalide/expiré → 401 (le portail
    déconnecte au lieu d'afficher un faux 403) ; valide → claims (RBAC)."""
    return auth_deps.bearer_identity(authorization, JWT_SECRET)


class AnonymizeIn(BaseModel):
    patient_name: str
    patient_id: str
    study_description: str = ""
    modality: str = "OT"


UPSTREAMS = {
    "imaging-service": "http://localhost:8003",
    "orthanc-pacs": "http://localhost:8042",
}


@app.get("/api/v1/routes", tags=["routage"])
def routes() -> dict:
    return {"upstreams": UPSTREAMS,
            "note": "C-STORE/C-FIND natifs via pynetdicom en v0.2 (ADR-0002)"}


@app.post("/api/v1/anonymize", tags=["anonymisation"])
def anonymize(body: AnonymizeIn, user: dict = Depends(current_user)) -> dict:
    """Anonymisation DICOM (profil Basic Application Level, PS3.15) :
    0010,0010 (nom) et 0010,0020 (id) remplacés par un pseudonyme HMAC."""
    pseudo = security.pseudonymize(body.patient_name, body.patient_id,
                                   salt="dicom-anonymization")
    return {
        "00100010": {"vr": "PN", "Value": [{"Alphabetic": "ANONYMOUS^" + pseudo[:8]}]},
        "00100020": {"vr": "LO", "Value": [pseudo[:16]]},
        "0008103E": {"vr": "LO", "Value": [body.study_description]},
        "00080060": {"vr": "CS", "Value": [body.modality]},
        "00120062": {"vr": "CS", "Value": ["YES"]},  # PatientIdentityRemoved
        "00120063": {"vr": "LO", "Value": ["MEDISUITE pseudonymization v1"]},
    }


@app.post("/api/v1/forward/study", tags=["routage"])
def forward(payload: dict) -> dict:
    """Mise en file d'un transfert d'étude vers Orthanc (mode dév : simulé)."""
    uid = payload.get("study_uid", "")
    if not uid:
        raise HTTPException(422, "study_uid requis")
    return {"study_uid": uid, "destination": "orthanc-pacs",
            "statut": "mis en file", "protocole": "C-STORE"}


@app.get("/api/v1/worklist", tags=["routage"])
def worklist(modality: str = "") -> list[dict]:
    """Worklist modality (MWL, subset DICOM JSON)."""
    demo = [("CT", "TDM cérébral — code AVC"), ("MR", "IRM prostatique"),
            ("US", "Écho abdominale"), ("CR", "Radio thorax")]
    return [{"00080060": {"vr": "CS", "Value": [m]},
             "0008103E": {"vr": "LO", "Value": [d]}}
            for m, d in demo if not modality or m == modality]
