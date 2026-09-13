"""Tests reporting-service."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "reporting-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
from medisuite_core import security
_tok = security.jwt_encode({"sub": "t", "role": "radiologue", "nom": "Dr Yao"},
                           "medisuite-dev-secret-change-in-prod")
HDR = {"Authorization": f"Bearer {_tok}"}
client = TestClient(app)


def test_templates():
    assert "radiologie" in client.get("/api/v1/templates").json()["templates"]


def test_generate_et_get():
    r = client.post("/api/v1/reports", json={
        "kind": "radiologie", "titre": "TDM thorax", "patient_nom": "KOUASSI Yao",
        "sections": {"indication": "bilan nodule", "conclusion": "suivi 3 mois"}},
        headers=HDR)
    assert r.status_code == 201
    rid = r.json()["id"]
    html = client.get(f"/api/v1/reports/{rid}")
    assert "TDM thorax" in html.text and "MEDISUITE" in html.text


def test_signature():
    rid = client.post("/api/v1/reports", json={
        "kind": "laboratoire", "titre": "NFS"}, headers=HDR).json()["id"]
    r = client.post(f"/api/v1/reports/{rid}/sign", headers=HDR)
    assert r.status_code == 200 and len(r.json()["signature"]) > 16


def test_kind_inconnu():
    r = client.post("/api/v1/reports", json={"kind": "x", "titre": "x"}, headers=HDR)
    assert r.status_code == 422
