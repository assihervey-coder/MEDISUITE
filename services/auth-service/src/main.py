"""auth-service — identité, JWT, MFA TOTP, RBAC (ADR-0009).

Endpoints : login/register/refresh/logout, gestion utilisateurs et rôles,
émission et vérification de tokens signés HS256 (clé partagée inter-services).
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
for p in ("packages/medisuite-core", "packages/clinical-rules"):
    sys.path.insert(0, str(ROOT / p))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from medisuite_core import security
from medisuite_core.db import Base, engine_for, init_db, new_id
from medisuite_core.http import create_service_app
from medisuite_core.rbac import PERMISSIONS, ROLES, can
from medisuite_core.seed import NOMS, PRENOMS_F, PRENOMS_M

app: FastAPI = create_service_app(
    "auth-service", "Authentification & Identité",
    "JWT HS256, MFA TOTP (RFC 6238), RBAC clinique fail-closed, sessions.",
    module_label="IAM")

engine = engine_for("auth-service")
JWT_SECRET = "medisuite-dev-secret-change-in-prod"  # Vault en production (ADR-0010)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    nom: Mapped[str] = mapped_column(String(80))
    prenoms: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(30), index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    totp_secret: Mapped[str | None] = mapped_column(String(40), nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    tentatives_echouees: Mapped[int] = mapped_column(Integer, default=0)


SessionLocal = init_db(engine, Base.metadata)


class LoginIn(BaseModel):
    email: str
    password: str
    totp_code: str | None = None


class UserIn(BaseModel):
    email: str
    nom: str
    prenoms: str
    role: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    nom: str
    prenoms: str
    role: str
    mfa_enabled: bool
    active: bool


def _get_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def seed() -> None:
    """Comptes de démonstration : admin, médecin, biologiste, radiologue,
    infirmier, data manager (écran Promoteur/DSMB — ecrf.export/lock)."""
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return
        demo = [
            ("admin@medisuite.ci", "Kouassi", "Sylvain", "administrateur"),
            ("medecin@chu-cocody.ci", "Koné", "Fatoumata", "medecin"),
            ("biologiste@chu-cocody.ci", "Traoré", "Ibrahim", "biologiste"),
            ("radiologue@chu-treichville.ci", "Yao", "Aristide", "radiologue"),
            ("infirmier@chu-cocody.ci", "Bamba", "Awa", "infirmier"),
            ("datamanager@medisuite.ci", "Gbagbo", "Nadège", "data_manager"),
        ]
        for email, nom, prenoms, role in demo:
            db.add(User(id=new_id(), email=email, nom=nom, prenoms=prenoms,
                        role=role, password_hash=security.hash_password("MediSuite2026!")))
        db.commit()


def current_user(authorization: str | None = Header(default=None)) -> dict:
    """Dépendance FastAPI : valide le Bearer JWT et retourne les claims."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "en-tête Authorization Bearer requis")
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], JWT_SECRET)
    except security.JWTError as exc:
        raise HTTPException(401, str(exc))


@app.get("/api/v1/permissions", tags=["RBAC"])
def list_permissions() -> dict:
    return {"permissions": PERMISSIONS,
            "roles": {r: sorted(p) for r, p in ROLES.items()}}


@app.post("/api/v1/auth/login", tags=["auth"])
def login(body: LoginIn) -> dict:
    seed()
    with SessionLocal() as db:
        user = _get_user(db, body.email)
        if not user or not user.active:
            raise HTTPException(401, "identifiants invalides")
        if not security.verify_password(body.password, user.password_hash):
            user.tentatives_echouees += 1
            db.commit()
            raise HTTPException(401, "identifiants invalides")
        if user.mfa_enabled:
            if not body.totp_code:
                raise HTTPException(428, "code TOTP requis (MFA activé)")
            if not user.totp_secret or not security.totp_verify(
                    user.totp_secret, body.totp_code):
                raise HTTPException(401, "code TOTP invalide")
        user.tentatives_echouees = 0
        db.commit()
        token = security.jwt_encode(
            {"sub": user.id, "email": user.email, "role": user.role,
             "nom": f"{user.nom} {user.prenoms}"},
            JWT_SECRET, expires_in_s=8 * 3600)
        return {"access_token": token, "token_type": "Bearer",
                "expires_in_s": 8 * 3600, "role": user.role}


@app.post("/api/v1/auth/refresh", tags=["auth"])
def refresh(user: dict = Depends(current_user)) -> dict:
    return {"access_token": security.jwt_encode(user, JWT_SECRET,
                                                expires_in_s=8 * 3600)}


@app.post("/api/v1/users", status_code=201, tags=["utilisateurs"])
def create_user(body: UserIn, user: dict = Depends(current_user)) -> UserOut:
    if not can(user.get("role", ""), "admin.users"):
        raise HTTPException(403, "permission admin.users requise")
    if body.role not in ROLES:
        raise HTTPException(422, f"rôle inconnu (choix : {sorted(ROLES)})")
    with SessionLocal() as db:
        if _get_user(db, body.email):
            raise HTTPException(409, "email déjà utilisé")
        u = User(id=new_id(), email=body.email.lower(), nom=body.nom,
                 prenoms=body.prenoms, role=body.role,
                 password_hash=security.hash_password(body.password))
        db.add(u)
        db.commit()
        return UserOut(id=u.id, email=u.email, nom=u.nom, prenoms=u.prenoms,
                       role=u.role, mfa_enabled=u.mfa_enabled, active=u.active)


@app.get("/api/v1/users", tags=["utilisateurs"])
def list_users(user: dict = Depends(current_user)) -> list[UserOut]:
    if not can(user.get("role", ""), "admin.users"):
        raise HTTPException(403, "permission admin.users requise")
    with SessionLocal() as db:
        users = db.scalars(select(User)).all()
        return [UserOut(id=u.id, email=u.email, nom=u.nom, prenoms=u.prenoms,
                        role=u.role, mfa_enabled=u.mfa_enabled, active=u.active)
                for u in users]


@app.post("/api/v1/auth/mfa/enroll", tags=["auth"])
def mfa_enroll(user: dict = Depends(current_user)) -> dict:
    """Active le MFA : génère un secret TOTP (à scanner dans une app d'auth)."""
    secret = security.totp_generate_secret()
    with SessionLocal() as db:
        u = db.get(User, user["sub"])
        if not u:
            raise HTTPException(404, "utilisateur introuvable")
        u.totp_secret = secret
        u.mfa_enabled = True
        db.commit()
    return {"secret_base32": secret,
            "otpauth": f"otpauth://totp/MEDISUITE:{u.email}?secret={secret}",
            "note": "vérifiez avec POST /api/v1/auth/login + totp_code"}


@app.get("/api/v1/auth/me", tags=["auth"])
def me(user: dict = Depends(current_user)) -> dict:
    return user
