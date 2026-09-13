#!/usr/bin/env bash
# 04-certs — certificat autosigné DEV pour l'arrêt TLS local (optionnel).
# Idempotent : les certificats existants ne sont jamais écrasés.
# ⚠️ DEV ONLY : en staging/prod, passer par la PKI du CHU (mTLS — voir
# security/hardening/tls/README.md et le plan pentest).
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

CERT_DIR="${MEDISUITE_ROOT}/local-deployment/certs"
need_cmd openssl

if [ -f "${CERT_DIR}/medisuite-local.crt" ] && [ -f "${CERT_DIR}/medisuite-local.key" ]; then
  ok "certificats déjà présents : ${CERT_DIR} (conservés)"
  exit 0
fi

log "génération d'un certificat autosigné dev (CN=medisuite.local, SAN local)"
mkdir -p "${CERT_DIR}"
openssl req -x509 -newkey rsa:2048 -sha256 -days 30 -nodes \
  -keyout "${CERT_DIR}/medisuite-local.key" \
  -out "${CERT_DIR}/medisuite-local.crt" \
  -subj "/C=CI/O=MEDISUITE DEV/CN=medisuite.local" \
  -addext "subjectAltName=DNS:medisuite.local,DNS:localhost,IP:127.0.0.1" \
  >/dev/null 2>&1
chmod 600 "${CERT_DIR}/medisuite-local.key"
chmod 644 "${CERT_DIR}/medisuite-local.crt"

ok "certificat dev généré (30 jours) : ${CERT_DIR}/medisuite-local.{crt,key}"
warn "certificat autosigné = confiance manuelle côté navigateur ; NE PAS utiliser en production"
