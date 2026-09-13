#!/usr/bin/env bash
# 03-env — génération de local-deployment/.env (secrets DEV uniquement).
# Idempotent : un .env existant n'est JAMAIS écrasé (le perdre = casser les
# données déjà chiffrées/scellées localement). Permissions 600 imposées.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

ENV_FILE="${MEDISUITE_ROOT}/local-deployment/.env"
need_cmd openssl

if [ -f "${ENV_FILE}" ]; then
  ok ".env existant conservé : ${ENV_FILE}"
else
  log "génération d'un .env local avec secrets aléatoires (openssl rand)"
  JWT="$(openssl rand -hex 32)"
  ORTHANC="$(openssl rand -hex 16)"
  PG="$(openssl rand -hex 16)"
  VAULT="medisuite-$(openssl rand -hex 8)"
  cat > "${ENV_FILE}" <<EOF
# MEDISUITE — secrets LOCAUX (DEV ONLY — ne jamais committer ni réutiliser).
# Généré par local-deployment/setup/03-env.sh — permissions 600 imposées.
MEDISUITE_JWT_SECRET=${JWT}
MEDISUITE_ORTHANC_PASSWORD=${ORTHANC}
MEDISUITE_POSTGRES_PASSWORD=${PG}
MEDISUITE_VAULT_TOKEN=${VAULT}
EOF
  ok ".env généré"
fi

chmod 600 "${ENV_FILE}"
ok "permissions imposées : $(stat -c '%a' "${ENV_FILE}") (600 attendu)"

# La compose minimale embarque ses identifiants de démonstration (medisuite-dev)
# : ce .env sert aux scripts (smoke, vault) et à toute variation locale.
log "rappel : la compose minimal.yml garde ses identifiants de démo internes (réseau docker isolé) — ce .env pilote les scripts, pas les conteneurs"

ok "environnement prêt — poursuivre avec 04-certs.sh"
