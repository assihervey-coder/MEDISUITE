"""Tests hl7-gateway : ACK auto, routage ADT/ORM/ORU/SIU."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "hl7-gateway" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

ADT = ("MSH|^~\\&|HIS|CHU|MEDISUITE|CHU|20260913090000||ADT^A08|MSG1|P|2.5\r"
       "PID|1||MS-2026-00001||KOUASSI^Yao||19850412|M")


def test_process_adt():
    r = client.post("/api/v1/process", json={"message": ADT}).json()
    assert r["type"] == "ADT^A08"
    assert "MSA|AA" in r["ack"]
    assert "patient-service" in r["destination"]


def test_message_sans_msh():
    assert client.post("/api/v1/process", json={"message": "garbage"}).status_code == 422


def test_queue():
    client.post("/api/v1/queue/push", json={"type": "ORM^O01"})
    s = client.get("/api/v1/queue/stats").json()
    assert s["compteurs"].get("ORM", 0) >= 1
