#!/usr/bin/env bash
# 08-up — démarrage de la stack minimale en conteneurs + attente des santés.
# Ports : gateway 8000 · orthanc 8042 · OHIF 3001 · HAPI 8090 · otel 4317/4318
#         vault 9000 · prometheus 9090 · grafana 3000 (cf. compose minimal.yml)
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

if ! docker_ready; then
  warn "docker absent — mode conteneurs indisponible ; utiliser le mode natif (make dev-up) 🟠"
  exit 0
fi
[ -f "${COMPOSE_FILE}" ] || die "compose introuvable : ${COMPOSE_FILE}"

log "docker compose up -d (stack medisuite)"
docker compose -f "${COMPOSE_FILE}" up -d || die "échec de démarrage — docker compose logs pour diagnostic"

FAIL=0
wait_http "http://localhost:8000/health" 120 "api-gateway (:8000)" || FAIL=1
wait_http "http://localhost:8042/system" 60  "orthanc-pacs (:8042)" || FAIL=1
wait_http "http://localhost:8090/fhir/metadata" 180 "hapi-fhir (:8090, premier démarrage long)" || FAIL=1
wait_http "http://localhost:9090/-/ready" 60 "prometheus (:9090)" || FAIL=1
wait_http "http://localhost:3000/api/health" 60 "grafana (:3000)" || FAIL=1
wait_http "http://localhost:3001/" 60 "ohif-viewer (:3001)" || FAIL=1

if [ "${FAIL}" = "0" ]; then
  ok "stack complète démarrée et saine"
else
  warn "stack démarrée avec des services en retard — consulter docker compose logs, relancer 08-up"
fi
ok "poursuivre avec 09-smoke.sh (vérification fonctionnelle)"
