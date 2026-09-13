"""Tests nephrology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "nephrology-service" / "src")):
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
    assert info["module"] == 16 and "nephrology-service" in info["service"]


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



def test_score_dfg_ckd_epi():
    r = client.post("/api/v1/scores/dfg_ckd_epi", json={'age': 68, 'sexe': 'M', 'creatinine_mgdl': 2.1}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_kdigo_mrc():
    r = client.post("/api/v1/scores/kdigo_mrc", json={'egfr': 32, 'albuminurie_mg_g': 180}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_kdigo_aki():
    r = client.post("/api/v1/scores/kdigo_aki", json={'creatinine_baseline': 1.0, 'creatinine_actuelle': 2.6, 'diurese_ml_kg_h': 0.4}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_ktv():
    r = client.post("/api/v1/scores/ktv", json={'uree_pre_mmol_l': 24, 'uree_post_mmol_l': 7.5, 'uf_total_l': 2.5, 'poids_post_kg': 68, 'duree_h': 4}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

