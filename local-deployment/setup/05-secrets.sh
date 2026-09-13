#!/usr/bin/env bash
# 05-secrets — injection des secrets locaux dans Vault (mode dev de la compose).
# Idempotent : `vault kv put` écrase proprement les mêmes chemins.
# Sauté proprement si docker/vault ne tournent pas (mode natif) — 🟠.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

ENV_FILE="${MEDISUITE_ROOT}/local-deployment/.env"
[ -f "${ENV_FILE}" ] || die ".env absent — exécuter 03-env.sh d'abord"
# shellcheck disable=SC1090
set -a; . "${ENV_FILE}"; set +a

if ! docker_ready; then
  warn "docker absent — secrets Vault non injectés (mode natif : les services lisent leurs variables d'environnement) 🟠"
  exit 0
fi
if ! docker ps --format '{{.Names}}' | grep -qx 'medisuite-vault-1'; then
  warn "conteneur vault non démarré (08-up le lancera) — relancer 05-secrets.sh après 08-up 🟠"
  exit 0
fi

log "injection des secrets dev dans Vault (kv/secret/medisuite/*)"
docker exec -e VAULT_TOKEN="${MEDISUITE_VAULT_TOKEN:-medisuite-dev-root-token}" medisuite-vault-1 \
  vault kv put secret/medisuite/local \
  jwt_secret="${MEDISUITE_JWT_SECRET:-}" \
  orthanc_password="${MEDISUITE_ORTHANC_PASSWORD:-}" \
  postgres_password="${MEDISUITE_POSTGRES_PASSWORD:-}" >/dev/null \
  || die "échec d'injection Vault (token dev invalide ?)"
ok "secrets écrits : secret/medisuite/local (jwt, orthanc, postgres)"
warn "vault mode DEV (in-memory) : re-sceller au redémarrage — migration cluster HA requise avant production (ADR-0010)"
