"""Tests auth-service : login, JWT, RBAC, MFA."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", str(ROOT / "services" / "auth-service" / "src")):
    sys.path.insert(0, p)

# BDD fraîche par run (principe v0.1 « idempotence ») : les tests mutent
# l'état persistant (MFA enrôlé, utilisateurs créés) — une base de dev
# polluée casserait toute ré-exécution locale. Le seed de démo se rejoue
# seul au boot sur une base vide ; en CI le fichier n'existe pas.
for _suffix in ("", "-wal", "-shm"):
    _db = ROOT / "data" / f"auth-service.db{_suffix}"
    if _db.exists():
        _db.unlink()

from fastapi.testclient import TestClient

from main import app, JWT_SECRET

client = TestClient(app)


def _login(email="medecin@chu-cocody.ci", password="MediSuite2026!"):
    return client.post("/api/v1/auth/login",
                       json={"email": email, "password": password})


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_login_ok():
    r = _login()
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "Bearer" and body["role"] == "medecin"
    from medisuite_core import security
    claims = security.jwt_decode(body["access_token"], JWT_SECRET)
    assert claims["role"] == "medecin"


def test_login_ko():
    assert _login(password="faux").status_code == 401
    assert _login(email="inconnu@x.ci").status_code == 401


def test_me_requires_jwt():
    assert client.get("/api/v1/auth/me").status_code == 401
    tok = _login().json()["access_token"]
    r = client.get("/api/v1/auth/me",
                   headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200 and r.json()["role"] == "medecin"


def test_create_user_rbac():
    tok_medecin = _login().json()["access_token"]
    r = client.post("/api/v1/users", json={
        "email": "nouveau@medisuite.ci", "nom": "Aka", "prenoms": "Test",
        "role": "pharmacien", "password": "Pass2026!"},
        headers={"Authorization": f"Bearer {tok_medecin}"})
    assert r.status_code == 403  # un médecin ne crée pas d'utilisateurs

    tok_admin = _login("admin@medisuite.ci").json()["access_token"]
    r = client.post("/api/v1/users", json={
        "email": "nouveau@medisuite.ci", "nom": "Aka", "prenoms": "Test",
        "role": "pharmacien", "password": "Pass2026!"},
        headers={"Authorization": f"Bearer {tok_admin}"})
    assert r.status_code == 201 and r.json()["role"] == "pharmacien"


def test_rôle_inconnu_rejeté():
    tok_admin = _login("admin@medisuite.ci").json()["access_token"]
    r = client.post("/api/v1/users", json={
        "email": "x@medisuite.ci", "nom": "N", "prenoms": "P",
        "role": "superhéro", "password": "Pass2026!"},
        headers={"Authorization": f"Bearer {tok_admin}"})
    assert r.status_code == 422


def test_mfa_enroll_et_login():
    tok = _login("infirmier@chu-cocody.ci").json()["access_token"]
    r = client.post("/api/v1/auth/mfa/enroll",
                    headers={"Authorization": f"Bearer {tok}"})
    secret = r.json()["secret_base32"]
    # login sans TOTP → 428
    assert client.post("/api/v1/auth/login", json={
        "email": "infirmier@chu-cocody.ci",
        "password": "MediSuite2026!"}).status_code == 428
    # login avec bon code TOTP
    import time, base64, hmac, struct, hashlib
    counter = int(time.time()) // 30
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    d = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = d[-1] & 0x0F
    code = f"{(struct.unpack('>I', d[off:off+4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"
    assert client.post("/api/v1/auth/login", json={
        "email": "infirmier@chu-cocody.ci", "password": "MediSuite2026!",
        "totp_code": code}).status_code == 200


def test_permissions_catalogue():
    r = client.get("/api/v1/permissions")
    assert "medecin" in r.json()["roles"]
