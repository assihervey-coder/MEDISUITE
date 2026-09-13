"""Tests integration-service : HL7 roundtrip, MLLP, FHIR, serveur HAPI (v0.4), OTel."""
import json
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "integration-service" / "src")):
    sys.path.insert(0, p)
from fastapi.testclient import TestClient
from main import app, JWT_SECRET, hapi as hapi_singleton
from medisuite_core import security
from medisuite_core import observability
client = TestClient(app)

_token = security.jwt_encode({"sub": "dr-yao", "role": "medecin",
                              "nom": "Dr Yao"}, JWT_SECRET)
HDR = {"Authorization": f"Bearer {_token}"}
_auditeur = security.jwt_encode({"sub": "aud-1", "role": "auditeur"}, JWT_SECRET)
HDR_AUDITEUR = {"Authorization": f"Bearer {_auditeur}"}

PATIENT = {"numero_dossier": "MS-2026-00042", "nom": "KOUASSI", "prenoms": "Yao",
           "date_naissance": "1985-04-12", "sexe": "M", "telephone": "+225 07 00 00 00 00"}

CAPABILITY = {"resourceType": "CapabilityStatement", "status": "active",
              "fhirVersion": "4.0.1", "format": ["application/fhir+json"]}


def _fake_hapi_opener(pages: dict, capture: list | None = None):
    """urlopen factice : sert `pages` par chemin d'URL ('/metadata', '/Patient'…)."""

    class _Resp:
        def __init__(self, payload):
            self._raw = json.dumps(payload).encode()

        def read(self):
            return self._raw

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def _open(req, timeout=None):
        if capture is not None:
            capture.append(req)
        path = req.full_url.split("/fhir", 1)[1] or "/"
        for prefix, payload in pages.items():
            if req.full_url.endswith(prefix) or path.startswith(prefix):
                return _Resp(payload)
        raise urllib.error.HTTPError(req.full_url, 404, "not found", {}, None)

    return _open


# ── HL7 / MLLP (v0.1) ─────────────────────────────────────────────────────────

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


# ── Serveur FHIR HAPI (v0.4) ──────────────────────────────────────────────────

def test_fhir_server_status_requires_auth():
    assert client.get("/api/v1/fhir/server/status").status_code == 403


def test_fhir_server_status_hors_ligne():
    def _down(req, timeout=None):
        raise urllib.error.URLError("connexion refusée")

    hapi_singleton._opener = _down
    hapi_singleton.timeout = 0.1
    try:
        r = client.get("/api/v1/fhir/server/status", headers=HDR)
        body = r.json()
        assert r.status_code == 200
        assert body["reachable"] is False and body["fhir_version"] is None
    finally:
        hapi_singleton._opener = None


def test_fhir_server_metadata_relay():
    hapi_singleton._opener = _fake_hapi_opener({"/metadata": CAPABILITY})
    try:
        r = client.get("/api/v1/fhir/server/metadata", headers=HDR)
        assert r.status_code == 200
        assert r.json()["fhirVersion"] == "4.0.1"
    finally:
        hapi_singleton._opener = None


def test_fhir_server_search_bundle():
    bundle = {"resourceType": "Bundle", "type": "searchset", "total": 1,
              "entry": [{"resource": {"resourceType": "Patient", "id": "p1"}}]}
    hapi_singleton._opener = _fake_hapi_opener({"/Patient": bundle})
    try:
        r = client.get("/api/v1/fhir/server/patients", params={"family": "KOUASSI"},
                       headers=HDR)
        assert r.status_code == 200
        assert r.json()["entry"][0]["resource"]["id"] == "p1"
    finally:
        hapi_singleton._opener = None


def test_fhir_server_create_patient():
    capture: list = []
    created = {"resourceType": "Patient", "id": "abc123",
               "meta": {"versionId": "1"}}
    hapi_singleton._opener = _fake_hapi_opener({"/Patient": created}, capture)
    try:
        r = client.post("/api/v1/fhir/server/patients", json=PATIENT, headers=HDR)
        assert r.status_code == 201
        body = r.json()
        assert body["id"] == "abc123" and body["resourceType"] == "Patient"
        # la ressource envoyée est bien un FHIR Patient (mapping médisuite→R4)
        payload = json.loads(capture[0].data.decode())
        assert payload["resourceType"] == "Patient"
        assert payload["name"][0]["family"] == "KOUASSI"
        # RBAC : auditeur (pas de patient.write) → 403 fail-closed
        ra = client.post("/api/v1/fhir/server/patients", json=PATIENT,
                         headers=HDR_AUDITEUR)
        assert ra.status_code == 403
    finally:
        hapi_singleton._opener = None


# ── Profils nationaux IOP-CI (ADR-0024, v0.5) ─────────────────────────────────

from medisuite_core import iop as iop_mod

PATIENT_IOP = {"identifiant_national": "CI2026AB1234", "nom": "KOUASSI",
               "prenoms": "Yao", "date_naissance": "1985-04-12", "sexe": "M",
               "cnam": "1234567890", "region": "Abidjan",
               "telephone": "+225 07 00 00 00 00"}


def test_iop_validators():
    assert iop_mod.validate_national_id("ci2026ab1234") == "CI2026AB1234"
    assert iop_mod.validate_cnam("1234567890") == "1234567890"
    assert iop_mod.validate_region("Abidjan") == "Abidjan"
    for bad in ("", "ABC", "MS-2026-00042", "a" * 17, "CI2026 0000", "0000"):
        try:
            iop_mod.validate_national_id(bad)
            assert False, f"devait rejeter {bad!r}"
        except iop_mod.IopValidationError:
            pass
    for bad_cnam in ("12345", "12345678901", "abcdefghij"):
        try:
            iop_mod.validate_cnam(bad_cnam)
            assert False, f"CNAM devait rejeter {bad_cnam!r}"
        except iop_mod.IopValidationError:
            pass
    try:
        iop_mod.validate_region("Bretagne")
        assert False
    except iop_mod.IopValidationError:
        pass


def test_iop_profiles_catalog():
    r = client.get("/api/v1/fhir/profiles")
    body = r.json()
    assert body["adr"] == "0024" and body["count"] == 4
    ids = {p["id"] for p in body["profiles"]}
    assert {"Patient-CI-IOP", "Observation-CI-IOP"} <= ids


def test_fhir_server_create_iop():
    capture: list = []
    created = {"resourceType": "Patient", "id": "iop42",
               "meta": {"versionId": "1"}}
    hapi_singleton._opener = _fake_hapi_opener({"/Patient": created}, capture)
    try:
        r = client.post("/api/v1/fhir/server/patients/iop", json=PATIENT_IOP,
                        headers=HDR)
        assert r.status_code == 201 and r.json()["id"] == "iop42"
        payload = json.loads(capture[0].data.decode())
        # profil national référencé + identifiant national en tête
        assert payload["meta"]["profile"] == [iop_mod.PROFILE_PATIENT]
        ident = payload["identifier"][0]
        assert ident["system"] == iop_mod.NATIONAL_OID
        assert ident["value"] == "CI2026AB1234" and ident["use"] == "official"
        # CNAM secondaire + région sanitaire (extension)
        assert payload["identifier"][1]["value"] == "1234567890"
        assert any(e["valueString"] == "Abidjan" for e in payload["extension"])
        # RBAC : auditeur → 403
        ra = client.post("/api/v1/fhir/server/patients/iop", json=PATIENT_IOP,
                         headers=HDR_AUDITEUR)
        assert ra.status_code == 403
        # non-conformité : identifiant national avec tirets (dossier local)
        bad = dict(PATIENT_IOP, identifiant_national="MS-2026-00042")
        rb = client.post("/api/v1/fhir/server/patients/iop", json=bad,
                         headers=HDR)
        assert rb.status_code == 422 and "CI-IOP" in rb.json()["detail"]
    finally:
        hapi_singleton._opener = None


# ── OpenTelemetry (v0.4) ──────────────────────────────────────────────────────

def test_traceparent_roundtrip():
    tp = observability.format_traceparent("a" * 32, "b" * 16)
    ctx = observability.parse_traceparent(tp)
    assert ctx == {"trace_id": "a" * 32, "parent_span_id": "b" * 16, "flags": "01"}
    # headers invalides → None (résilience W3C)
    assert observability.parse_traceparent(None) is None
    assert observability.parse_traceparent("") is None
    assert observability.parse_traceparent("01-abc") is None
    assert observability.parse_traceparent("00-" + "0" * 32 + "-" + "b" * 16 + "-01") is None
    assert observability.parse_traceparent("00-" + "g" * 32 + "-" + "b" * 16 + "-01") is None


def test_middleware_creates_span_and_propagates():
    tracer = observability.get_tracer("integration-service")
    before = tracer.snapshot()["pending_spans"]
    tp_in = observability.format_traceparent("c" * 32, "d" * 16)
    # route métier (403 attendu sans auth — le middleware passe avant) ;
    # /health et /ready sont des routes de bruit sans span depuis ADR-0025
    r = client.get("/api/v1/fhir/server/status", headers={"traceparent": tp_in})
    assert r.status_code == 403
    # le middleware poursuit la trace entrante (même trace_id)
    tp_out = r.headers.get("traceparent", "")
    assert tp_out.startswith("00-" + "c" * 32 + "-")
    # et un span a été enregistré
    after = tracer.snapshot()["pending_spans"]
    assert after == before + 1


def test_noise_routes_produce_no_span():
    """ADR-0025 : les sondes de vie ne génèrent pas de span."""
    tracer = observability.get_tracer("integration-service")
    before = tracer.snapshot()["pending_spans"]
    for path in ("/health", "/ready"):
        r = client.get(path)
        assert r.status_code == 200
        assert r.headers.get("X-Service-Name") == "integration-service"
    assert tracer.snapshot()["pending_spans"] == before


def test_sampling_root_ratio_deterministic():
    """ADR-0025 : décision racine déterministe sur le trace_id."""
    tracer = observability.Tracer("smp", sampling_ratio=0.0)
    for _ in range(2):  # même décision à chaque appel (pas d'aléatoire)
        s = tracer.start_server_span("HTTP GET /x")
        assert s.sampled is False
        assert s.attributes["otel.sampling.decision"] == "ratio_dropped"
    tracer_full = observability.Tracer("smp", sampling_ratio=1.0)
    s = tracer_full.start_server_span("HTTP GET /x")
    assert s.sampled is True
    assert s.attributes["otel.sampling.decision"] == "ratio_sampled"


def test_sampling_parent_based():
    """ADR-0025 : la décision du parent W3C prévaut (ParentBased)."""
    drop = observability.Tracer("smp", sampling_ratio=0.0)
    keep = observability.Tracer("smp", sampling_ratio=1.0)
    s1 = drop.start_server_span(
        "x", traceparent=observability.format_traceparent("a" * 32, "b" * 16, "01"))
    assert s1.sampled is True and s1.attributes["otel.sampling.decision"] == "parent_sampled"
    s2 = keep.start_server_span(
        "x", traceparent=observability.format_traceparent("c" * 32, "d" * 16, "00"))
    assert s2.sampled is False and s2.attributes["otel.sampling.decision"] == "parent_unsampled"
    # flags réservés (bit 1) : le bit 0 seul décide
    s3 = drop.start_server_span(
        "x", traceparent=observability.format_traceparent("e" * 32, "f" * 16, "03"))
    assert s3.sampled is True


def test_sampling_always_on_errors():
    """ADR-0025 : un span en erreur est TOUJOURS conservé."""
    tracer = observability.Tracer("smp", sampling_ratio=0.0)
    ok = tracer.start_server_span("HTTP GET /ok")
    ok.end(ok=True)
    tracer.record(ok)  # non échantillonné → compté comme écarté
    ko = tracer.start_server_span("HTTP GET /ko")
    ko.end(ok=False)
    tracer.record(ko)  # erreur → conservé malgré ratio 0.0
    snap = tracer.snapshot()
    assert snap["pending_spans"] == 1
    assert snap["sampling_dropped"] == 1
    assert snap["sampling_ratio"] == 0.0


def test_sampling_unsampled_propagates_flags_00():
    """ADR-0025 : la décision est propagée honnêtement en aval."""
    observability._default = observability.Tracer("prop", sampling_ratio=0.0)
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        app = FastAPI()

        @app.middleware("http")
        async def _mw(request, call_next):
            tracer = observability.get_tracer("prop")
            if request.url.path in tracer.noise_routes:
                resp = await call_next(request)
                resp.headers["X-Skip"] = "1"
                return resp
            span = tracer.start_server_span(
                f"HTTP {request.method} {request.url.path}",
                traceparent=request.headers.get("traceparent"))
            resp = await call_next(request)
            span.end(ok=resp.status_code < 500)
            tracer.record(span)
            resp.headers["traceparent"] = observability.format_traceparent(
                span.trace_id, span.span_id, "01" if span.sampled else "00")
            return resp

        @app.get("/api/x")
        def x():
            return {"ok": True}

        c = TestClient(app)
        r = c.get("/api/x")
        assert r.headers["traceparent"].endswith("-00")
        r = c.get("/health")
        assert r.headers.get("X-Skip") == "1"
    finally:
        observability._default = None


def test_sampling_ratio_env_fail_open(monkeypatch):
    """ADR-0025 : env invalide → 1.0 (ne jamais supprimer la télémétrie)."""
    monkeypatch.setenv("MEDISUITE_OTEL_SAMPLING_RATIO", "nonsense")
    assert observability.Tracer("env1").sampling_ratio == 1.0
    monkeypatch.setenv("MEDISUITE_OTEL_SAMPLING_RATIO", "0.25")
    assert observability.Tracer("env2").sampling_ratio == 0.25
    monkeypatch.setenv("MEDISUITE_OTEL_SAMPLING_RATIO", "12")
    assert observability.Tracer("env3").sampling_ratio == 1.0
    monkeypatch.setenv("MEDISUITE_OTEL_SAMPLING_RATIO", "-3")
    assert observability.Tracer("env4").sampling_ratio == 0.0


def test_otlp_export_payload():
    capture: list = []

    class _Resp:
        def read(self):
            return b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def _open(req, timeout=None):
        capture.append(req)
        return _Resp()

    tracer = observability.Tracer("test-svc", endpoint="http://otel-fake:4318/v1/traces")
    tracer._opener = _open
    s1 = tracer.start_server_span("HTTP GET /x", traceparent=None)
    s1.set_attribute("http.status_code", 200)
    s1.end(ok=True)
    s2 = tracer.start_server_span("HTTP POST /y")
    s2.end(ok=False)
    tracer.record(s1)
    tracer.record(s2)
    assert tracer.export_now() == 2
    payload = json.loads(capture[0].data.decode())
    rs = payload["resourceSpans"][0]
    svc = [a for a in rs["resource"]["attributes"] if a["key"] == "service.name"]
    assert svc[0]["value"]["stringValue"] == "test-svc"
    spans = rs["scopeSpans"][0]["spans"]
    assert len(spans) == 2
    assert spans[0]["traceId"] == s1.trace_id and len(spans[0]["traceId"]) == 32
    assert spans[1]["status"]["code"] == "STATUS_CODE_ERROR"
