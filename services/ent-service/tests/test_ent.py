"""Tests ent-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "ent-service" / "src")):
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
    assert info["module"] == 19 and "ent-service" in info["service"]


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



def test_score_pta_oms():
    r = client.post("/api/v1/scores/pta_oms", json={'seuils_db_4freq': {'500': 35, '1000': 40, '2000': 50, '4000': 55}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_lund_mackay():
    r = client.post("/api/v1/scores/lund_mackay", json={'scores_sinusiens': {'maxillaire_d': 2, 'maxillaire_g': 1, 'ethmoide_ant_d': 2, 'ethmoide_ant_g': 1, 'ethmoide_post_d': 1, 'ethmoide_post_g': 0, 'sphenoid_d': 0, 'sphenoid_g': 0, 'frontal_d': 1, 'frontal_g': 0, 'ostium_d': 2, 'ostium_g': 1, 'cells': 1}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_bppv():
    r = client.post("/api/v1/scores/bppv", json={'hallpike_droit': True, 'hallpike_gauche': False, 'vertige_latence': True, 'fatigue': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

