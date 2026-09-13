"""Tests neurology-service : santé, module-info, scores, cas cliniques."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "neurology-service" / "src")):
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
    assert info["module"] == 13 and "neurology-service" in info["service"]


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



def test_score_aspects():
    r = client.post("/api/v1/scores/aspects", json={'scores_regions': {'caudate': 1, 'insula': 0, 'internal_capsule': 1, 'M1': 1, 'M2': 1, 'M3': 1, 'M4': 1, 'M5': 1, 'M6': 1, 'lenticular': 1}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_nihss():
    r = client.post("/api/v1/scores/nihss", json={'items': {'niveau_conscience': 1, 'regard': 1, 'champ_visuel': 0, 'facial': 2, 'moteur_bras_g': 2, 'moteur_bras_d': 0, 'moteur_jambe_g': 2, 'moteur_jambe_d': 0, 'ataxie': 0, 'sensoriel': 1, 'langage': 0, 'dysarthrie': 1, 'extinction': 0}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_mmse():
    r = client.post("/api/v1/scores/mmse", json={'items': {'orientation_temporelle': 4, 'orientation_spatiale': 4, 'memoire_immédiate': 3, 'attention_calcul': 2, 'rappel': 1, 'langage': 5, 'praxie_visuoconstructive': 0}}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide


def test_score_mcdonald():
    r = client.post("/api/v1/scores/mcdonald", json={'dissemination_espace': True, 'dissemination_temps': False, 'bande_oligoclonales': True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["resultat"]  # résultat structuré non vide

