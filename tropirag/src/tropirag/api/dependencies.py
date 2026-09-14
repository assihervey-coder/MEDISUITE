"""Dépendances FastAPI."""
from __future__ import annotations

from fastapi import Header

from tropirag.core.config import get_config


async def require_api_key(x_api_key: str = Header(default="")) -> None:
    cfg = get_config()
    if cfg.security.require_api_key and cfg.security.api_key and x_api_key != cfg.security.api_key:
        from fastapi import HTTPException

        raise HTTPException(401, "API key invalide")
