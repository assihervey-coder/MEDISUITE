"""Tests laboratory-service : workflow complet, valeurs critiques, Westgard, HL7."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules",
          str(ROOT / "services" / "laboratory-service" / "src")):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient

from main import app
from medisuite_core import security

JWT_SECRET = "medisuite-dev-secret-change-in-prod"
_token = security.jwt_encode({"sub": "test-user", "role": "biologiste",
                              "nom": "Dr Traoré"}, JWT_SECRET)
HDR = {"Authorization": f"Bearer {_token}"}
client = TestClient(app)


def _order(analyte="hemoglobine", urgent=False):
    r = client.post("/api/v1/orders", json={
        "patient_id": "pat0001", "patient_dossier": "MS-2026-00001",
        "patient_nom": "KOUASSI Yao", "analyte": analyte,
        "prescripteur": "Dr Koné", "urgent": urgent}, headers=HDR)
    assert r.status_code == 201
    return r.json()


def test_workflow_complet():
    o = _order()
    assert o["statut"] == "ORDERED"
    # prélèvement
    r = client.post(f"/api/v1/orders/{o['id']}/collect", headers=HDR)
    assert r.status_code == 200 and r.json()["barcode"].startswith("LAB-")
    # résultat entré par l'automate
    r = client.post(f"/api/v1/orders/{o['id']}/results",
                    json={"valeur": 13.2, "resultat_precedent": 13.8}, headers=HDR)
    body = r.json()
    assert body["flag"] == "normal" and body["notification_critique"] is False
    rid = body["id"]
    # validation biologiste
    r = client.post(f"/api/v1/results/{rid}/validate", headers=HDR)
    assert r.status_code == 200
    msg = r.json()["message_hl7_oru"]
    assert "MSH|^~\\&" in msg and "ORU^R01" in msg and "OBX" in msg
    # le workflow ne peut pas repartir en arrière
    assert client.post(f"/api/v1/orders/{o['id']}/collect",
                       headers=HDR).status_code == 409


def test_valeur_critique_alerte():
    o = _order("potassium")
    client.post(f"/api/v1/orders/{o['id']}/collect", headers=HDR)
    r = client.post(f"/api/v1/orders/{o['id']}/results",
                    json={"valeur": 7.4}, headers=HDR).json()
    assert r["critical"] is True and r["notification_critique"] is True
    assert r["flag"] == "abnormal_high"


def test_delta_check():
    o = _order("hemoglobine")
    client.post(f"/api/v1/orders/{o['id']}/collect", headers=HDR)
    r = client.post(f"/api/v1/orders/{o['id']}/results", json={
        "valeur": 8.0, "resultat_precedent": 13.5}, headers=HDR).json()
    assert r["delta_pct"] and r["delta_pct"] > 40  # écart majeur


def test_analyte_inconnu():
    r = client.post("/api/v1/orders", json={
        "patient_id": "p", "analyte": "chimiokine-XYZ"}, headers=HDR)
    assert r.status_code == 422


def test_westgard_rejet():
    r = client.post("/api/v1/qc/run", json={
        "analyte": "glucose", "moyenne": 100, "ecart_type": 5,
        "valeurs": [100, 118]}, headers=HDR).json()
    assert r["violations"] == ["1_3s"] and r["decision"].startswith("rejet")


def test_westgard_accepte_et_levey_jennings():
    qc = client.post("/api/v1/qc/run", json={
        "analyte": "glucose", "moyenne": 100, "ecart_type": 5,
        "valeurs": [99, 101, 100.5, 98.5]}, headers=HDR).json()
    assert qc["samples_released"] is True
    lj = client.get(f"/api/v1/qc/{qc['qc_id']}/levey-jennings").json()
    assert len(lj) == 4 and all("z" in p for p in lj)


def test_hl7_roundtrip_orm_oru():
    o = _order("glucose", urgent=True)
    orm = client.get(f"/api/v1/hl7/orm/{o['id']}").json()["message"]
    assert "ORM^O01" in orm
    # l'automate répond avec un ORU — le service doit le parser
    oru = ("MSH|^~\\&|ANALYZER|LAB|MEDISUITE|LAB|20260913090000||ORU^R01|MSG1|P|2.5\r"
           "PID|1||MS-2026-00001||KOUASSI^Yao\r"
           "OBX|1|NM|1558-6^Glucose||95|mg/dL|70-110|N|||F")
    r = client.post("/api/v1/hl7/oru", json={"message": oru}).json()
    assert r["type"] == "ORU^R01" and r["valeur"] == 95.0
    assert r["patient_dossier"] == "MS-2026-00001"


def test_oru_type_invalide():
    r = client.post("/api/v1/hl7/oru", json={"message": "MSH|^~\\&|X|X|X|X|"
                                            "20260913||ADT^A08|1|P|2.5"})
    assert r.status_code == 422
