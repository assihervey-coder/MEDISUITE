"""Tests cardiology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "cardiology-service" / "src")):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient

from main import app
from medisuite_core import security

_token = security.jwt_encode({"sub": "t", "role": "medecin"},
                             "medisuite-dev-secret-change-in-prod")
HDR = {"Authorization": f"Bearer {_token}"}
client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_module_info():
    info = client.get("/module-info").json()
    assert info["module"] == 8 and "cardiology-service" in info["service"]


def test_cases_crud():
    r = client.get("/api/v1/cases", headers=HDR)
    assert r.status_code == 200 and len(r.json()) >= 3
    r = client.post("/api/v1/cases", json={
        "patient_id": "patX", "titre": "Cas de test", "date": "2026-09-13"},
        headers=HDR)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.post(f"/api/v1/cases/{cid}/close",
                       headers=HDR).json()["statut"] == "clos"
    assert client.get("/api/v1/cases").status_code == 403  # RBAC fail-closed



def test_score_chads2ds2vasc():
    r = client.post("/api/v1/scores/chads2ds2vasc", json={'insuffisance_cardiaque': True, 'hta': True, 'diabete': False, 'avc_ou_atcd_thrombose': False, 'maladie_vasculaire': True, 'age': 74, 'sexe_feminin': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_heart_score():
    r = client.post("/api/v1/scores/heart_score", json={'anamnese': 'modérément', 'ecg': 'non-spécifique', 'age': 58, 'facteurs_risque': 2, 'troponine': 'x1'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_nyha():
    r = client.post("/api/v1/scores/nyha", json={'classe_tolerances': 'effort_ordinaire'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_framingham():
    r = client.post("/api/v1/scores/framingham", json={'age': 60, 'cholesterol_mgdl': 240, 'hdl_mgdl': 45, 'pas': 145, 'hta_traitee': True, 'fumeur': True, 'diabete': False, 'sexe': 'M'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

