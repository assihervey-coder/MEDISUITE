#!/usr/bin/env bash
# 07-images — construction/téléchargement des images de la compose minimale.
# Idempotent : build et pull sont cache-friendly (relance = no-op si à jour).
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

if ! docker_ready; then
  warn "docker absent — construction des images sautée (mode natif) 🟠"
  exit 0
fi
need_cmd docker
[ -f "${COMPOSE_FILE}" ] || die "compose introuvable : ${COMPOSE_FILE}"

log "pull des images tierces versionnées (Orthanc, HAPI, PG16, OTel, Vault, Prometheus, Grafana)"
docker compose -f "${COMPOSE_FILE}" pull --ignore-buildable \
  || warn "pull incomplet (réseau ?) — les builds locaux peuvent continuer 🟠"

log "build des images MEDISUITE (5 services cœur + OHIF/nginx)"
docker compose -f "${COMPOSE_FILE}" build api-gateway auth-service patient-service imaging-service laboratory-service ohif-viewer \
  || die "échec de build — vérifier Dockerfile.service et le contexte"

ok "images prêtes — poursuivre avec 08-up.sh"
