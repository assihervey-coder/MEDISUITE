"""Tests geriatrics-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "geriatrics-service" / "src")):
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
    assert info["module"] == 25 and "geriatrics-service" in info["service"]


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



def test_score_fried():
    r = client.post("/api/v1/scores/fried", json={'fatigue_epuisee': True, 'perte_poids_recente': True, 'faible_prise_force': True, 'marche_lente': False, 'activite_physique_basse': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_tug():
    r = client.post("/api/v1/scores/tug", json={'secondes': 22.5, 'marche_canne': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_braden():
    r = client.post("/api/v1/scores/braden", json={'perception': 2, 'humidite': 2, 'activite': 1, 'mobilite': 2, 'nutrition': 2, 'frottement': 2}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_mna_sf():
    r = client.post("/api/v1/scores/mna_sf", json={'declin_repas': True, 'perte_poids': True, 'mobilite_reduite': False, 'stress_maladie': True, 'neuropsychologique': False, 'imc_value': 20.5}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_beers():
    r = client.post("/api/v1/scores/beers", json={'medicaments': ['diazépam', 'ibuprofène', 'metformine']}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

