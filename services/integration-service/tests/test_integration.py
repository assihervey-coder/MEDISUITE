"""Tests integration-service : HL7 roundtrip, MLLP, FHIR."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "integration-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

PATIENT = {"numero_dossier": "MS-2026-00042", "nom": "KOUASSI", "prenoms": "Yao",
           "date_naissance": "1985-04-12", "sexe": "M", "telephone": "+225 07 00 00 00 00"}


def test_routes():
    assert "ADT" in client.get("/api/v1/routes").json()["routes"]


def test_hl7_roundtrip():
    built = client.post("/api/v1/hl7/build/adt", json=PATIENT).json()
    parsed = client.post("/api/v1/hl7/parse", json={"message": built["message"]}).json()
    assert parsed["type"] == "ADT^A08" and parsed["patient_id"] == "MS-2026-00042"
    ack = client.post("/api/v1/hl7/ack", json={"message": built["message"]}).json()["ack"]
    assert "MSA|AA" in ack


def test_mllp_hex_roundtrip():
    hexs = client.post("/api/v1/mllp/frame", json={"message": "MSH|^~\\&|A"}).json()["hex"]
    out = client.post("/api/v1/mllp/unframe", json={"hex": hexs}).json()["message"]
    assert out == "MSH|^~\\&|A"


def test_fhir_bundle():
    b = client.get("/api/v1/fhir/patients", params={"n": 4}).json()
    assert b["resourceType"] == "Bundle" and b["total"] == 4
