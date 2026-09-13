"""Tests pneumology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "pneumology-service" / "src")):
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
    assert info["module"] == 9 and "pneumology-service" in info["service"]


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



def test_score_gold():
    r = client.post("/api/v1/scores/gold", json={'mmc_pct': 65, 'dyspnee_mrc': 2, 'exacerbations_12m': 2, 'hospitalisation_exacerbation': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_stop_bang():
    r = client.post("/api/v1/scores/stop_bang", json={'snorring': True, 'fatigue': True, 'apnee_obseree': True, 'pression_arterielle_haute': True, 'imc_over_35': False, 'age_over_50': True, 'tour_cou_over_40cm': False, 'sexe_masculin': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_tb_oms():
    r = client.post("/api/v1/scores/tb_oms", json={'toux_2sem_plus': True, 'fievre': True, 'sueurs_nocturnes': True, 'perte_poids': True, 'contact_tb': False, 'vih_positif': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_spirometrie():
    r = client.post("/api/v1/scores/spirometrie", json={'fev1_l': 1.3, 'fvc_l': 3.4, 'fev1_theo_pct': 38}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

