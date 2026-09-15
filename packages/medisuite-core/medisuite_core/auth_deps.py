"""Dépendances FastAPI partagées : identité à partir du Bearer JWT.

Sémantique (correctif — les jetons périmés ne doivent PAS masquer la cause
derrière un faux 403 RBAC) :

  - aucun en-tête ``Authorization`` → identité anonyme (``sub: anon``) :
    les endpoints publics continuent de répondre et le RBAC fail-closed
    reste maître de l'autorisation ;
  - jeton présent mais **invalide ou expiré** → HTTP 401 : le portail
    intercepte 401 pour déconnecter proprement (« session expirée —
    reconnectez-vous ») au lieu d'afficher « accès refusé » trompeur ;
  - jeton valide → claims (``sub``, ``role``, …) — l'autorisation reste
    entièrement au RBAC (``medisuite_core.rbac.can``).

Le module est volontairement séparé de ``security.py`` (cœur stdlib-pur,
auditable ligne à ligne — IEC 62304) : ici uniquement le collage FastAPI.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException

from medisuite_core import security

DEV_SECRET = "medisuite-dev-secret-change-in-prod"


def bearer_identity(authorization: Annotated[str | None, Header()] = None,
                    secret: str = DEV_SECRET) -> dict:
    """Dépendance d'identité : anon / 401 (jeton périmé) / claims."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return {"sub": "anon", "role": ""}
    try:
        return security.jwt_decode(authorization.split(" ", 1)[1], secret)
    except security.JWTError as e:
        raise HTTPException(401, f"jeton invalide ou expiré ({e}) — reconnectez-vous")
