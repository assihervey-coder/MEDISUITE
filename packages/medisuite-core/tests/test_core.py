"""Tests du noyau medisuite-core : sécurité, RBAC, audit chaîné, HL7, FHIR."""
import time

import pytest

from medisuite_core import security, rbac
from medisuite_core.audit_chain import HashChainLedger
from medisuite_core import hl7, fhir


# ---------------------------------------------------------------- scrypt / JWT

def test_password_hash_roundtrip():
    h = security.hash_password("MotDePasse!2026")
    assert h.startswith("scrypt$")
    assert security.verify_password("MotDePasse!2026", h)
    assert not security.verify_password("faux", h)


def test_password_hash_unique_salt():
    a = security.hash_password("x")
    b = security.hash_password("x")
    assert a != b  # sel unique


def test_jwt_roundtrip():
    tok = security.jwt_encode({"sub": "user1", "role": "medecin"}, "secret-dev")
    payload = security.jwt_decode(tok, "secret-dev")
    assert payload["sub"] == "user1" and payload["role"] == "medecin"


def test_jwt_signature_invalide():
    tok = security.jwt_encode({"sub": "u"}, "secret-a")
    with pytest.raises(security.JWTError):
        security.jwt_decode(tok, "secret-b")


def test_jwt_expire():
    tok = security.jwt_encode({"sub": "u"}, "s", expires_in_s=-1)
    with pytest.raises(security.JWTError):
        security.jwt_decode(tok, "s")


def test_jwt_refuse_alg_downgrade():
    # un token forgé avec "none" doit échouer à la vérification HS256
    with pytest.raises(security.JWTError):
        security.jwt_decode("eyJhbGciOiJub25lIn0.e30.x", "s")


def test_totp_rfc6238():
    secret = security.totp_generate_secret()
    # code de la fenêtre courante accepté
    import base64, hashlib, hmac, struct
    counter = int(time.time()) // 30
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = digest[-1] & 0x0F
    code = f"{(struct.unpack('>I', digest[off:off+4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"
    assert security.totp_verify(secret, code)


def test_pseudonymisation_deterministe():
    a = security.pseudonymize("KOUASSI", "Yao", salt="s")
    b = security.pseudonymize("kouassi", "yao", salt="s")
    assert a == b and len(a) == 64


# ---------------------------------------------------------------- RBAC

def test_rbac_fail_closed():
    assert not rbac.can("role_inexistant", "patient.read")
    with pytest.raises(PermissionError):
        rbac.require("patient", "patient.read")


def test_rbac_matrice_clinique():
    assert rbac.can("biologiste", "lab.validate")
    assert not rbac.can("infirmier", "prescription.write")
    assert rbac.can("medecin", "ai.infer")


# ---------------------------------------------------------------- audit chaîné

def test_chaine_integrite():
    ledger = HashChainLedger()
    for i in range(10):
        ledger.append("user", "medecin", "patient.read", f"patient:{i}")
    ok, bad = ledger.verify()
    assert ok and bad is None


def test_chaine_detecte_alteration():
    ledger = HashChainLedger()
    for i in range(5):
        ledger.append("user", "medecin", "lab.order", f"order:{i}")
    # altération rétroactive
    ledger.events[2].action = "action_falsifiée"
    ok, bad = ledger.verify()
    assert not ok and bad == 2


def test_chaine_genesis():
    ledger = HashChainLedger()
    e = ledger.append("sys", "system", "boot", "service:auth")
    assert e.prev_hash == "0" * 64 and len(e.hash) == 64


# ---------------------------------------------------------------- HL7 v2

PATIENT = {"numero_dossier": "MS-2026-00001", "nom": "KOUASSI", "prenoms": "Yao",
           "date_naissance": "1985-04-12", "sexe": "M", "telephone": "+225 07 07 07 07 07"}


def test_hl7_parse_type_message():
    msg = hl7.parse(hl7.build_adt_a08(PATIENT))
    assert msg.message_type == "ADT^A08"
    assert msg.field("PID", 3, 0, 0) == "MS-2026-00001"
    assert msg.field("PID", 5, 0, 0) == "KOUASSI"


def test_hl7_orm_obr():
    msg = hl7.parse(hl7.build_orm_o01({"id": "CMD1", "code_examen": "718-7",
                                       "libelle_examen": "Hémoglobine"}))
    assert msg.message_type == "ORM^O01"
    assert "718-7" in msg.field("OBR", 4, 0, 0)


def test_hl7_oru_obx_flag():
    res = {"loinc": "718-7", "analyse": "Hémoglobine", "valeur": "6.9",
           "unite": "g/dL", "dans_reference": False}
    msg = hl7.parse(hl7.build_oru_r01(res, PATIENT))
    assert msg.message_type == "ORU^R01"
    assert msg.field("OBX", 8, 0, 0) == "A"  # anormal


def test_hl7_ack():
    msg = hl7.parse(hl7.build_adt_a08(PATIENT))
    ack = hl7.parse(hl7.ack_for(msg))
    assert ack.message_type.startswith("ACK")
    assert ack.field("MSA", 1, 0, 0) == "AA"


def test_mllp_frame_roundtrip():
    msg = hl7.build_adt_a08(PATIENT)
    framed = hl7.mllp_frame(msg)
    assert framed.startswith(b"\x0b") and framed.endswith(b"\x1c\r")
    assert hl7.mllp_unframe(framed) == msg


def test_hl7_siu():
    msg = hl7.parse(hl7.build_siu_s12({"id": "RDV1"}, PATIENT))
    assert msg.message_type == "SIU^S12" and msg.segment("AIS") is not None


# ---------------------------------------------------------------- FHIR R4

def test_fhir_patient():
    p = {"id": "pat1", "nom": "KONÉ", "prenoms": "Aya", "sexe": "F",
         "date_naissance": "1990-01-01", "numero_dossier": "MS-1", "cnam": "CNAM-123",
         "telephone": "+225 01 02 03 04 05"}
    r = fhir.patient_to_fhir(p)
    assert r["resourceType"] == "Patient" and r["name"][0]["family"] == "KONÉ"
    assert any(i["value"] == "CNAM-123" for i in r["identifier"])


def test_fhir_observation_loinc():
    o = {"id": "o1", "loinc": "718-7", "analyse": "Hémoglobine", "valeur": 13.5,
         "unite": "g/dL", "valide": True}
    r = fhir.observation_to_fhir(o, "pat1")
    assert r["resourceType"] == "Observation"
    assert r["code"]["coding"][0]["code"] == "718-7"
    assert r["status"] == "final"


def test_fhir_bundle():
    b = fhir.bundle([fhir.patient_to_fhir({"id": "1", "nom": "X"})])
    assert b["resourceType"] == "Bundle" and b["total"] == 1
