"""Middleware — authentification par API key (header X-API-Key ou Authorization)."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

PUBLIC_PATHS = ("/", "/mobile", "/mobile/", "/map", "/map.html", "/health",
                "/api/docs", "/api/v1/health", "/openapi.json", "/metrics",
                "/favicon.ico")


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str) -> None:
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        if not self.api_key:  # clé vide = auth désactivée (dev)
            return await call_next(request)
        path = request.url.path
        if path.startswith(PUBLIC_PATHS) or path.startswith("/assets"):
            return await call_next(request)
        key = request.headers.get("X-API-Key") or ""
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            key = auth[7:]
        if key != self.api_key:
            return JSONResponse({"detail": "API key invalide ou absente (X-API-Key)"},
                                status_code=401)
        return await call_next(request)
