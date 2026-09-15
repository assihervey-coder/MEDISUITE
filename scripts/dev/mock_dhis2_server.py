#!/usr/bin/env python3
"""Récepteur DHIS2 simulé — répétition générale avant serveur MSP-CI réel.

Double usage :
  1. VALIDATION E2E DE L'EXPORT : pointe TROPIRAG_DHIS2_BASE_URL vers ce
     récepteur (TROPIRAG_DHIS2_USERNAME/PASSWORD) — la chaîne complète
     surveillance → export → file offline → push transport est exercée
     sans toucher au serveur national.
  2. RÉPÉTITION GÉNÉRALE MSP-CI : le jour du branchement réel, le même
     scénario est rejoué avec l'URL du serveur DHIS2 du Ministère.

Reproduit l'API DHIS2 consommée par TropiRAG :
  GET  /api/system/ping     → ping (health)
  POST /api/dataValueSets   → résumé d'import DHIS2 (importCount, status)

Réponses conformes au contrat DHIS2 : Basic auth exigée, corps JSON
dataValueSets validé sommairement (dataElement/orgUnit/period/value),
résumé d'import renvoyé avec httpStatusCode 200.
"""
from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RECEIVED: list[dict] = []  # payloads acceptés (vérifiables après coup)


class _Handler(BaseHTTPRequestHandler):
    server_version = "MockDHIS2/2.41"

    def log_message(self, *args) -> None:  # silence (logs via print contrôlé)
        return

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self) -> bool:
        h = self.headers.get("Authorization", "")
        if not h.startswith("Basic "):
            return False
        try:
            user, _, _pwd = base64.b64decode(h[6:]).decode("utf-8").partition(":")
            return bool(user)
        except Exception:
            return False

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/system/ping"):
            self._json(200, {"ok": True, "system": "DHIS2 mock MSP-CI"})
        else:
            self._json(404, {"httpStatusCode": 404, "status": "ERROR",
                             "message": f"route inconnue : {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/api/dataValueSets"):
            self._json(404, {"httpStatusCode": 404, "status": "ERROR",
                             "message": f"route inconnue : {self.path}"})
            return
        if not self._auth_ok():
            self._json(401, {"httpStatusCode": 401, "status": "ERROR",
                             "message": "Authentication failed"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"httpStatusCode": 400, "status": "ERROR",
                             "message": "corps JSON invalide"})
            return

        values = payload.get("dataValues") or []
        valid = [v for v in values
                 if v.get("dataElement") and v.get("orgUnit")
                 and v.get("period") and v.get("value") is not None]
        invalid = len(values) - len(valid)

        RECEIVED.append(payload)
        print(f"[{datetime.now(timezone.utc):%H:%M:%S}] dataValueSets accepté : "
              f"{len(valid)} valeurs ({payload.get('orgUnit')}, "
              f"{len({v['period'] for v in valid})} période(s)) — total reçus : {len(RECEIVED)}",
              flush=True)
        # Contrat DHIS2 : ImportSummary
        self._json(200, {
            "httpStatusCode": 200, "status": "OK",
            "importOptions": payload.get("importOptions") or {},
            "importCount": {"imported": len(valid), "updated": 0,
                            "ignored": invalid, "deleted": 0},
            "dataSetComplete": payload.get("completeDate") or "",
            "responseType": "ImportSummary",
        })


def main() -> int:
    ap = argparse.ArgumentParser(description="Récepteur DHIS2 simulé (MSP-CI rehearsal)")
    ap.add_argument("--port", type=int, default=11440)
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), _Handler)
    print(f"Mock DHIS2 en écoute sur {srv.server_address} — "
          f"POST /api/dataValueSets, GET /api/system/ping")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\narrêt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
