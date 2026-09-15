"""Tests patient-service : CRUD, FHIR, consentements, RBAC fail-closed."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "patient-service" / "src")):
    sys.path.insert(0, p)

# BDD fraîche par run (principe v0.1 « idempotence ») — les patients de
# démo se re-seedent seuls au boot ; en CI le fichier n'existe pas.
for _suffix in ("", "-wal", "-shm"):
    _db = ROOT / "data" / f"patient-service.db{_suffix}"
    if _db.exists():
        _db.unlink()

from fastapi.testclient import TestClient

from main import app
from medisuite_core import security

JWT_SECRET = "medisuite-dev-secret-change-in-prod"
_token = security.jwt_encode({"sub": "test-user", "role": "medecin"}, JWT_SECRET)
HDR = {"Authorization": f"Bearer {_token}"}
client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_rbac_fail_closed():
    """Sans JWT : aucune lecture ni écriture du dossier patient (403)."""
    assert client.get("/api/v1/patients").status_code == 403
    r = client.post("/api/v1/patients", json={
        "nom": "X", "prenoms": "Y", "sexe": "M", "date_naissance": "2000-01-01"})
    assert r.status_code == 403


def test_jwt_expire_reponse_401_pas_403():
    """Jeton périmé → 401 (le portail déconnecte et affiche « session expirée »)
    au lieu d'un faux 403 « permission requise » qui masquait la cause réelle."""
    import time as _time

    expired = security.jwt_encode(
        {"sub": "test-user", "role": "medecin",
         "exp": int(_time.time()) - 10}, JWT_SECRET)
    r = client.get("/api/v1/patients",
                   headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401
    assert "expiré" in r.json()["detail"].lower()


def test_jwt_altere_reponse_401():
    """Jeton falsifié (signature invalide) → 401, jamais 200 ni 403 ambigu."""
    forged = _token[:-4] + "bEEF"
    r = client.get("/api/v1/patients",
                   headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


def test_seed_patients():
    r = client.get("/api/v1/patients", headers=HDR)
    assert r.status_code == 200
    patients = r.json()
    assert len(patients) >= 10
    p = patients[0]
    assert p["numero_dossier"].startswith("MS-") and "age" in p and "pseudonyme" in p


def test_recherche():
    r = client.get("/api/v1/patients", params={"q": "MS-2026-00001"}, headers=HDR)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_create_et_get():
    r = client.post("/api/v1/patients", json={
        "nom": "GBAMIE", "prenoms": "Rachelle", "sexe": "F",
        "date_naissance": "1995-08-20", "commune": "Yopougon",
        "cnam": "CNAM-555555"}, headers=HDR)
    assert r.status_code == 201
    pid = r.json()["id"]
    got = client.get(f"/api/v1/patients/{pid}", headers=HDR).json()
    assert got["nom"] == "GBAMIE" and got["age"] >= 30


def test_sexe_invalide():
    r = client.post("/api/v1/patients", json={
        "nom": "X", "prenoms": "Y", "sexe": "Z", "date_naissance": "2000-01-01"},
        headers=HDR)
    assert r.status_code == 422


def test_fhir():
    patients = client.get("/api/v1/patients", headers=HDR).json()
    r = client.get(f"/api/v1/patients/{patients[0]['id']}/fhir", headers=HDR)
    assert r.json()["resourceType"] == "Patient"


def test_encounter_et_condition():
    patients = client.get("/api/v1/patients", headers=HDR).json()
    pid = patients[0]["id"]
    r = client.post(f"/api/v1/patients/{pid}/encounters", json={
        "date": "2026-09-13", "motif": "céphalées chroniques",
        "prescripteur": "Dr Koné"}, headers=HDR)
    assert r.status_code == 201
    r = client.post(f"/api/v1/patients/{pid}/conditions", json={
        "cim10": "G43.9", "libelle": "Migraine sans aura"}, headers=HDR)
    assert r.status_code == 201 and r.json()["cim10"] == "G43.9"
    assert len(client.get(f"/api/v1/patients/{pid}/encounters",
                          headers=HDR).json()) == 1


def test_consentement_ia():
    patients = client.get("/api/v1/patients", headers=HDR).json()
    pid = patients[0]["id"]
    r = client.post(f"/api/v1/patients/{pid}/consent",
                    json={"consent_ia": True}, headers=HDR)
    assert r.json()["consent_ia"] is True
    # révocation RGPD immédiate
    r = client.post(f"/api/v1/patients/{pid}/consent",
                    json={"consent_ia": False}, headers=HDR)
    assert r.json()["consent_ia"] is False
