"""Tests urology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "urology-service" / "src")):
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
    assert info["module"] == 21 and "urology-service" in info["service"]


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



def test_score_ipss():
    r = client.post("/api/v1/scores/ipss", json={'frequence_nocturne': 3, 'frequence_2h': 4, 'retenue': 2, 'jets_faibles': 3, 'straining': 2, 'incomplets': 3}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_gleason():
    r = client.post("/api/v1/scores/gleason", json={'primaire': 4, 'secondaire': 3}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_renal_score():
    r = client.post("/api/v1/scores/renal_score", json={'ray_cm': 4.5, 'endophytique_pct': 60, 'near_urothelium': '4-7mm', 'anterieur_posterieur': 'p', 'polar': '2'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_pirads():
    r = client.post("/api/v1/scores/pirads", json={'lesions': [{'zone': 'périphérique', 't2': 2, 'dw': 4}]}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

