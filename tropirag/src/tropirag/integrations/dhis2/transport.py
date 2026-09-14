"""Transport DHIS2 — envoi httpx optionnel, jamais implicite.

Le transport n'est actif QUE si ``base_url`` + ``username`` sont configurés
(configs/integrations/dhis2.yaml ou TROPIRAG_DHIS2_BASE_URL). Sinon, la file
offline continue d'accumuler — aucun appel réseau n'est tenté.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from tropirag.integrations.dhis2.settings import Dhis2Config


class TransportNotConfigured(Exception):
    """Le serveur DHIS2 n'est pas configuré — la file offline reste maître."""


@dataclass(slots=True)
class PushReport:
    ok: bool
    status_code: int | None = None
    detail: str = ""


class Dhis2Transport:
    """POST /api/dataValueSets au serveur DHIS2 du MSP-CI."""

    def __init__(self, cfg: Dhis2Config, http_post=None) -> None:
        """``http_post`` injectable pour les tests (signature : url, json, auth,
        timeout, verify) → objet réponse .status_code/.text."""
        self.cfg = cfg
        self._post = http_post or self._default_post

    @staticmethod
    def _default_post(url, json, auth, timeout, verify):  # pragma: no cover — réseau réel
        import httpx

        resp = httpx.post(url, json=json, auth=auth, timeout=timeout, verify=verify)
        return resp

    def push(self, payload: dict) -> PushReport:
        if not self.cfg.transport_ready:
            raise TransportNotConfigured(
                "DHIS2 : base_url/username absents — configurer "
                "TROPIRAG_DHIS2_BASE_URL ou configs/integrations/dhis2.yaml")
        password = os.environ.get(self.cfg.password_env, "")
        try:
            resp = self._post(
                f"{self.cfg.base_url.rstrip('/')}/api/dataValueSets",
                json=payload,
                auth=(self.cfg.username or "", password),
                timeout=self.cfg.timeout_s,
                verify=self.cfg.verify_tls,
            )
            ok = 200 <= int(resp.status_code) < 300
            return PushReport(ok=ok, status_code=int(resp.status_code),
                              detail=getattr(resp, "text", "")[:500])
        except Exception as e:  # réseau indisponible — la file reprendra
            return PushReport(ok=False, status_code=None, detail=str(e)[:300])
