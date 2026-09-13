"""Client Orthanc — PACS réel (REST + relais DICOMweb). v0.2, stdlib uniquement.

Connecteur du imaging-service vers un Orthanc de production (ADR 0006) :
statut système, liste d'études, relais QIDO-RS. Zéro dépendance externe
(urllib + base64), conforme à la contrainte « stdlib d'abord » du repo.

Configuration par variables d'environnement :
- MEDISUITE_ORTHANC_URL      (défaut http://localhost:8042)
- MEDISUITE_ORTHANC_USER     (défaut medisuite)
- MEDISUITE_ORTHANC_PASSWORD (défaut medisuite-dev)
- MEDISUITE_ORTHANC_TIMEOUT  (défaut 3.0 s)

Dégradation gracieuse : aucune exception ne remonte à l'API pour un Orthanc
hors ligne — `ping()` retourne False et `pacs_status` signale
reachable=false (exigence d'exploitation hospitalière : l'imagerie locale
reste consultable même quand le PACS central est en maintenance).
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request


class OrthancError(RuntimeError):
    """Orthanc injoignable ou réponse invalide."""


class OrthancClient:
    """Client REST Orthanc minimal et testable (injection d'opener)."""

    def __init__(self, url: str | None = None, user: str | None = None,
                 password: str | None = None, timeout: float | None = None,
                 opener=None) -> None:
        self.url = (url or os.environ.get(
            "MEDISUITE_ORTHANC_URL", "http://localhost:8042")).rstrip("/")
        self.user = user or os.environ.get("MEDISUITE_ORTHANC_USER", "medisuite")
        self.password = password or os.environ.get(
            "MEDISUITE_ORTHANC_PASSWORD", "medisuite-dev")
        self.timeout = float(timeout if timeout is not None
                             else os.environ.get("MEDISUITE_ORTHANC_TIMEOUT", 3.0))
        self._opener = opener  # injection pour tests (urllib.request.urlopen par défaut)

    # ── couche transport ──────────────────────────────────────────────────────
    def _get(self, path: str):
        req = urllib.request.Request(self.url + path)
        token = base64.b64encode(
            f"{self.user}:{self.password}".encode()).decode()
        req.add_header("Authorization", "Basic " + token)
        req.add_header("Accept", "application/json")
        urlopen = self._opener or urllib.request.urlopen
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except OrthancError:
            raise
        except Exception as exc:  # URLError, TimeoutError, OSError, JSONDecode…
            raise OrthancError(
                f"Orthanc injoignable ({self.url}) : {exc}") from exc

    # ── API haut niveau ───────────────────────────────────────────────────────
    def ping(self) -> bool:
        """True si /system répond — jamais d'exception."""
        try:
            return bool(self.system().get("Version"))
        except OrthancError:
            return False

    def system(self) -> dict:
        """GET /system — version, capacité de stockage, plugins."""
        data = self._get("/system")
        return data if isinstance(data, dict) else {}

    def studies(self, limit: int = 20) -> list[dict]:
        """GET /studies (+ expansion légère) → fiches d'études simplifiées."""
        ids = self._get("/studies")
        if not isinstance(ids, list):
            return []
        out: list[dict] = []
        for sid in ids[:max(0, int(limit))]:
            try:
                d = self._get(f"/studies/{sid}")
            except OrthancError:
                continue  # étude disparue entre liste et détail : toléré
            tags = d.get("MainDicomTags", {})
            parent = d.get("PatientMainDicomTags", {})
            out.append({
                "orthanc_id": sid,
                "study_uid": tags.get("StudyInstanceUID", ""),
                "patient_id": parent.get("PatientID", ""),
                "patient_nom": parent.get("PatientName", ""),
                "date": tags.get("StudyDate", ""),
                "description": tags.get("StudyDescription", ""),
                "series": len(d.get("Series", [])),
            })
        return out

    def dicomweb_studies(self, query: str = "") -> list[dict]:
        """Relais QIDO-RS : GET /dicom-web/studies[?query] — attributs DICOM JSON.

        query : chaîne brute après « ? » (ex. ``limit=10&Modality=MG``)."""
        suffix = f"?{query}" if query else ""
        data = self._get(f"/dicom-web/studies{suffix}")
        return data if isinstance(data, list) else []
