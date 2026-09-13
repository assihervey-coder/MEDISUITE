"""Tests imaging-service : DICOMweb STOW/QIDO/WADO, workflow compte-rendu."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "imaging-service" / "src")):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient

from main import app
from medisuite_core import security

JWT_SECRET = "medisuite-dev-secret-change-in-prod"
_token = security.jwt_encode({"sub": "test-user", "role": "radiologue",
                              "nom": "Dr Yao"}, JWT_SECRET)
HDR = {"Authorization": f"Bearer {_token}"}
client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_stow_puis_qido():
    # STOW-RS : dépôt d'une étude (format DICOM JSON simplifié)
    r = client.post("/dicom-web/studies", json={
        "00100020": {"Value": ["pat0001"]},
        "00100010": {"Value": [{"Alphabetic": "KOUASSI Yao"}]},
        "00080060": {"Value": ["CT"]},
        "0008103E": {"Value": ["Scanner thoracique"]},
        "00080020": {"Value": ["20260913"]}})
    assert r.status_code == 201
    uid = r.json()["00081190"]["Value"][0].split("/")[-1]

    # QIDO-RS : l'étude doit apparaître dans la recherche
    studies = client.get("/dicom-web/studies").json()
    assert any(s["0020000D"]["Value"][0] == uid for s in studies)

    # WADO-RS : métadonnées
    m = client.get(f"/dicom-web/studies/{uid}/metadata").json()
    assert m["00080060"]["Value"] == ["CT"]


def test_series():
    seed_studies = client.get("/api/v1/studies", headers=HDR).json()
    assert seed_studies  # seed exécuté
    s = seed_studies[0]
    series = client.get(f"/dicom-web/studies/{s['study_uid']}/series").json()
    assert len(series) >= 1


def test_workflow_compte_rendu():
    s = client.get("/api/v1/studies", headers=HDR).json()[0]
    # rédaction sans signature
    r = client.post(f"/api/v1/studies/{s['id']}/report", json={
        "impression": "Nodule apical droit 9 mm",
        "conclusion": "Nodule solide — Fleischner : CT 3-6 mois"}, headers=HDR)
    assert r.status_code == 201 and r.json()["signe"] is False
    got = client.get(f"/api/v1/studies/{s['id']}/report").json()
    assert "Fleischner" in got["conclusion"]


def test_connecteurs():
    r = client.get("/api/v1/integrations").json()
    assert "orthanc" in r and "ohif" in r
