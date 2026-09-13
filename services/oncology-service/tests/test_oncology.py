"""Tests oncology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "oncology-service" / "src")):
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
    assert info["module"] == 3 and "oncology-service" in info["service"]


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



def test_score_birads():
    r = client.post("/api/v1/scores/birads", json={'masse': True, 'microcalcifications': 'suspectes', 'asymetrie': False, 'aire_axillaire': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_fleischner():
    r = client.post("/api/v1/scores/fleischner", json={'nodule_mm': 9, 'risque_eleve': False, 'nodule_solide': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_lung_rads():
    r = client.post("/api/v1/scores/lung_rads", json={'nodule_mm': 12, 'croissance': True, 'nodules_solid_mass': False, 'ganglions_suspects': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_tnm_breast():
    r = client.post("/api/v1/scores/tnm_breast", json={'t_taille_cm': 3.2, 'n_ganglionnaire': 'cN1', 'm_metastase': False, 'grade_histologique': 2}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_roma():
    r = client.post("/api/v1/scores/roma", json={'ca125': 45, 'he4': 120, 'menopausee': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_ecog():
    r = client.post("/api/v1/scores/ecog", json={'karnofsky': 70}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

