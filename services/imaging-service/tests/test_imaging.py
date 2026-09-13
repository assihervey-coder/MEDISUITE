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


# ── v0.2 : client PACS Orthanc réel (opener factice, aucun serveur requis) ──
import json as _json
import urllib.error as _urlerror

import orthanc_client
from orthanc_client import OrthancClient, OrthancError


def _fake_opener(pages: dict):
    """urlopen factice : sert `pages` par chemin d'URL ('/system', '/studies'…)."""

    class _Resp:
        def __init__(self, payload):
            self._raw = _json.dumps(payload).encode()

        def read(self):
            return self._raw

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def _open(req, timeout=None):
        path = "/" + req.full_url.split("/", 3)[3]
        if path not in pages:
            raise _urlerror.URLError(f"404 : {path}")
        return _Resp(pages[path])

    return _open


def test_orthanc_client_system():
    oc = OrthancClient(url="http://pacs-fake:8042", user="u", password="p",
                       opener=_fake_opener({"/system": {"Version": "1.12.4",
                                                        "Name": "MEDISUITE-PACS"}}))
    assert oc.system()["Version"] == "1.12.4"
    assert oc.ping() is True


def test_orthanc_client_ping_hors_ligne():
    def _down(req, timeout=None):
        raise _urlerror.URLError("connexion refusée")

    oc = OrthancClient(url="http://127.0.0.1:1", timeout=0.1, opener=_down)
    assert oc.ping() is False


def test_orthanc_client_studies_expansion():
    pages = {
        "/studies": ["sid1", "sid2"],
        "/studies/sid1": {"MainDicomTags": {"StudyInstanceUID": "1.2.3",
                                            "StudyDate": "20260913",
                                            "StudyDescription": "MG bilatérale"},
                          "PatientMainDicomTags": {"PatientID": "pat0007",
                                                   "PatientName": "TRAORE Awa"},
                          "Series": ["s1", "s2", "s3"]},
        "/studies/sid2": {"MainDicomTags": {}, "PatientMainDicomTags": {},
                          "Series": []},
    }
    oc = OrthancClient(url="http://pacs-fake:8042", opener=_fake_opener(pages))
    rows = oc.studies(limit=5)
    assert rows[0]["patient_nom"] == "TRAORE Awa"
    assert rows[0]["series"] == 3
    assert rows[1]["orthanc_id"] == "sid2"


def test_orthanc_client_qido_relay():
    qido = [{"0020000D": {"vr": "UI", "Value": ["1.2.3"]}}]
    oc = OrthancClient(url="http://pacs-fake:8042",
                       opener=_fake_opener({"/dicom-web/studies?limit=10&Modality=MG": qido}))
    assert oc.dicomweb_studies("limit=10&Modality=MG")[0]["0020000D"]["Value"][0] == "1.2.3"


def test_pacs_status_hors_ligne_ne_crash_pas(monkeypatch):
    import main
    monkeypatch.setattr(main._oc, "OrthancClient",
                        lambda: OrthancClient(url="http://127.0.0.1:1", timeout=0.1))
    r = client.get("/api/v1/pacs/status")
    assert r.status_code == 200
    assert r.json()["reachable"] is False


def test_pacs_status_avec_pacs(monkeypatch):
    import main

    class _Stub:
        url = "http://orthanc-fake:8042"

        def system(self):
            return {"Version": "1.12.4", "Name": "MEDISUITE-PACS",
                    "DicomAet": "MEDISUITE", "PatientCount": 3, "StudyCount": 7}

    monkeypatch.setattr(main._oc, "OrthancClient", lambda: _Stub())
    body = client.get("/api/v1/pacs/status").json()
    assert body["reachable"] is True
    assert body["version"] == "1.12.4"
    assert body["etudes"] == 7


def test_pacs_studies_502_si_injoignable(monkeypatch):
    import main

    class _Down:
        def studies(self, limit=20):
            raise OrthancError("PACS down")

    monkeypatch.setattr(main._oc, "OrthancClient", lambda: _Down())
    assert client.get("/api/v1/pacs/studies").status_code == 502
