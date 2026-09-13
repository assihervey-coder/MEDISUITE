"""Tests anesthesia-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "anesthesia-service" / "src")):
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
    assert info["module"] == 24 and "anesthesia-service" in info["service"]


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



def test_score_sofa():
    r = client.post("/api/v1/scores/sofa", json={'respiration_pa02_fio2': 250, 'plaquettes_kul': 90, 'map_mmhg_ou_vasopresseurs': 'MAP<70', 'gcs': 13, 'bilirubine_mgdl': 1.8, 'creatinine_mgdl': 2.2}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_stop_bang():
    r = client.post("/api/v1/scores/stop_bang", json={'snorring': True, 'fatigue': False, 'apnee_obseree': True, 'pression_arterielle_haute': True, 'imc_over_35': True, 'age_over_50': False, 'tour_cou_over_40cm': True, 'sexe_masculin': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_gcs():
    r = client.post("/api/v1/scores/gcs", json={'ouverture_yeux': 'ordre', 'reponse_verbale': 'confus', 'reponse_motrice': 'retrait'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

