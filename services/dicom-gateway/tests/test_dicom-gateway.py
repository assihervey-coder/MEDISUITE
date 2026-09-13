"""Tests dicom-gateway."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "dicom-gateway" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)


def test_routes():
    assert "orthanc-pacs" in client.get("/api/v1/routes").json()["upstreams"]


def test_anonymize_supprime_identite():
    r = client.post("/api/v1/anonymize", json={
        "patient_name": "KOUASSI^Yao", "patient_id": "MS-1",
        "study_description": "TDM", "modality": "CT"}).json()
    assert "KOUASSI" not in str(r)
    assert r["00120062"]["Value"] == ["YES"]
    assert r["00100020"]["Value"][0] != "MS-1"


def test_worklist():
    wl = client.get("/api/v1/worklist").json()
    assert len(wl) == 4
    wl_ct = client.get("/api/v1/worklist", params={"modality": "CT"}).json()
    assert len(wl_ct) == 1
