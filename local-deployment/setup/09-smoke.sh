#!/usr/bin/env bash
# 09-smoke — vérification fonctionnelle des deux modes d'exécution.
# Mode natif : smoke de run_all (38 services SQLite).
# Mode conteneurs : sondes HTTP des endpoints clés de la compose minimale.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

log "— smoke mode natif (38 services) —"
if [ -x "${MEDISUITE_ROOT}/.venv/bin/python" ]; then
  venved python3 "${MEDISUITE_ROOT}/services/smoke_test.py" \
    || warn "smoke natif incomplet — certains services ne répondent pas 🟠"
else
  warn "venv absente (01-python.sh) — smoke natif sauté 🟠"
fi

log "— smoke mode conteneurs —"
if docker_ready && docker ps --format '{{.Names}}' | grep -q '^medisuite-api-gateway-1$'; then
  FAIL=0
  wait_http "http://localhost:8000/health" 30 "gateway /health" || FAIL=1
  wait_http "http://localhost:8042/system" 30 "orthanc /system" || FAIL=1
  wait_http "http://localhost:8090/fhir/metadata" 30 "hapi /fhir/metadata" || FAIL=1
  [ "${FAIL}" = "0" ] && ok "santé conteneurs : 3/3 sondes OK" \
    || warn "au moins une sonde conteneur en échec 🟠"
else
  warn "stack conteneurs non démarrée (08-up) — sondes conteneurs sautées 🟠"
fi

ok "smoke terminé — poursuivre avec 10-verify.sh"
