"""Sécurité : mots de passe scrypt, JWT HS256, TOTP (RFC 6238).

Tout est implémenté avec la bibliothèque standard Python pour être
**auditable ligne à ligne** — exigence IEC 62304 (logiciel de niveau C).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time

# ---------------------------------------------------------------- clés/base64

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)

# ---------------------------------------------------------------- scrypt

_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1


def hash_password(password: str) -> str:
    """Hache un mot de passe avec scrypt → 'scrypt$n$r$p$salt$hash'."""
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode(), salt=salt,
                        n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=32)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Vérification à temps constant (résiste aux timing attacks)."""
    try:
        algo, n, r, p, salt_hex, hash_hex = stored.split("$")
        if algo != "scrypt":
            return False
        dk = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex),
                            n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, TypeError):
        return False

# ---------------------------------------------------------------- JWT HS256

def jwt_encode(payload: dict, secret: str, expires_in_s: int = 3600) -> str:
    """Encode un JWT HS256 signé (RFC 7519). Claims standard ajoutés si absents."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    body = {"iat": now, "exp": now + expires_in_s, "jti": secrets.token_hex(8), **payload}
    signing_input = f"{b64url_encode(json.dumps(header).encode())}." \
                    f"{b64url_encode(json.dumps(body).encode())}"
    sig = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{b64url_encode(sig)}"


class JWTError(Exception):
    pass


def jwt_decode(token: str, secret: str) -> dict:
    """Décode et vérifie un JWT HS256. Lève JWTError si invalide/expiré."""
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        signing_input = f"{head_b64}.{body_b64}"
        expected = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
            raise JWTError("signature invalide")
        header = json.loads(b64url_decode(head_b64))
        if header.get("alg") != "HS256":
            raise JWTError("algorithme non autorisé (alg downgrade interdit)")
        payload = json.loads(b64url_decode(body_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise JWTError("token expiré")
        return payload
    except (ValueError, json.JSONDecodeError) as exc:
        raise JWTError(f"token malformé: {exc}") from exc

# ---------------------------------------------------------------- TOTP (RFC 6238)

def totp_generate_secret() -> str:
    """Secret base32 de 160 bits pour l'application d'authentification."""
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def _totp_at(secret: str, counter: int) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000
    return f"{code:06d}"


def totp_verify(secret: str, code: str, window: int = 1, period: int = 30) -> bool:
    """Vérifie un code TOTP avec tolérance ±window périodes (drift horloge)."""
    counter = int(time.time()) // period
    return any(hmac.compare_digest(_totp_at(secret, counter + d), code)
               for d in range(-window, window + 1))

# ---------------------------------------------------------------- divers

def generate_api_key(prefix: str = "msk") -> str:
    """Clé API pour les intégrations machines (analyteurs, PACS)."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def pseudonymize(*identifiers: str, salt: str) -> str:
    """Pseudonymisation RGPD : HMAC-SHA256 irréversible sur l'identité.

    Utilisée pour les flux inter-services et la recherche sans exposer l'identité.
    """
    joined = "|".join(sorted(identifiers)).lower().strip()
    return hmac.new(salt.encode(), joined.encode(), hashlib.sha256).hexdigest()
