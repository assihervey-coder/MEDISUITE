"""Tests rheumatology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "rheumatology-service" / "src")):
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
    assert info["module"] == 20 and "rheumatology-service" in info["service"]


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



def test_score_das28():
    r = client.post("/api/v1/scores/das28", json={'tender_count': 12, 'swollen_count': 8, 'vsr_mm_h': 55, 'santé_globale_0_100': 70}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_basdai():
    r = client.post("/api/v1/scores/basdai", json={'fatigue': 6, 'douleur_cervicale_dos': 7, 'douleur_peripherique': 4, 'douleur_sensibilite': 5, 'raideur_matinale_intensite': 6, 'raideur_matinale_duree_h': 1.5}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_sledaik():
    r = client.post("/api/v1/scores/sledaik", json={'criteres': {'arthrite': True, 'eruption_cutanee': True, 'protéinurie': True, 'faible_complément': True}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_kellgren():
    r = client.post("/api/v1/scores/kellgren", json={'pincement': True, 'osteophytes': 'net', 'sclerosis': True, 'deformite': False}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

