"""Tests emergency-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "emergency-service" / "src")):
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
    assert info["module"] == 26 and "emergency-service" in info["service"]


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



def test_score_esi():
    r = client.post("/api/v1/scores/esi", json={'niveau_ressources': 1, 'facteur_risque_haut': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_ctmp():
    r = client.post("/api/v1/scores/ctmp", json={'score': 3}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_qsofa():
    r = client.post("/api/v1/scores/qsofa", json={'freq_resp': 26, 'pas_systolique': 92, 'gcs_ou_avpu': 'V'}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_parkland():
    r = client.post("/api/v1/scores/parkland", json={'poids_kg': 65, 'pct_sbc': 25, 'heures_depuis_brule': 2}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_curbs65():
    r = client.post("/api/v1/scores/curbs65", json={'confusion': False, 'uree_mmol_l': 8.2, 'freq_resp': 28, 'pas_systolique': 105, 'age': 71}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_shock_index():
    r = client.post("/api/v1/scores/shock_index", json={'pouls': 125, 'pas_systolique': 95}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

