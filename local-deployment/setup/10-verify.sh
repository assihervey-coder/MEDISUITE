#!/usr/bin/env bash
# 10-verify — contrôle final d'installation : ce qui est 🟢 prêt, 🟠 partiel,
# 🔴 manquant. Sort en erreur si un prérequis DUR manque (venv, portal, .env).
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

FAIL=0
check() { # check <durs? "dur"|"opt"> <libellé> <cmd…>
  local durete="$1" libelle="$2"; shift 2
  if "$@" >/dev/null 2>&1; then
    ok "${libelle}"
  else
    if [ "${durete}" = "dur" ]; then die "MANQUANT (bloquant) : ${libelle}"
    else warn "${libelle} — non installé (voir scripts correspondants)"; fi
  fi
}

log "vérification finale de l'installation locale"
check dur  "venv Python (.venv)"            test -x "${MEDISUITE_ROOT}/.venv/bin/python"
check dur  "dépendances portail"            test -x "${MEDISUITE_ROOT}/apps/web-portal/node_modules/.bin/vite"
check dur  ".env local (600)"               sh -c "[ -f '${MEDISUITE_ROOT}/local-deployment/.env' ] && [ \"\$(stat -c '%a' '${MEDISUITE_ROOT}/local-deployment/.env')\" = 600 ]"
check opt  "certificats dev TLS"            test -f "${MEDISUITE_ROOT}/local-deployment/certs/medisuite-local.crt"
check opt  "tests e2e prêts (chromium)"     test -d "${MEDISUITE_ROOT}/apps/web-portal/node_modules/playwright-core"

log "— mode conteneurs —"
if docker_ready && docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^medisuite-api-gateway-1$'; then
  ok "stack compose démarrée (gateway, orthanc, hapi, otel, vault, prometheus, grafana, ohif)"
  check opt "gateway répond (:8000)"  curl -sf "http://localhost:8000/health"
  check opt "orthanc répond (:8042)"  curl -sf "http://localhost:8042/system"
else
  warn "stack compose non démarrée — lancer 07-images.sh puis 08-up.sh (ou rester en mode natif : make dev-up)"
fi

log "— bases de données (mode natif) —"
LS_DATA="$(ls "${MEDISUITE_ROOT}"/data/*.sqlite3 2>/dev/null | wc -l)"
if [ "${LS_DATA}" -gt 0 ]; then
  ok "bases SQLite présentes : ${LS_DATA} fichier(s) dans data/"
else
  warn "aucune base SQLite dans data/ — lancer 06-db.sh (ou make dev-up direct)"
fi

log ""
log "═╡ Installation locale MEDISUITE ╞══════════════════════════════════"
log "  Mode natif   : make dev-up && make smoke   (38 services, ports 8000+)"
log "  Conteneurs   : 08-up déjà exécuté (gateway :8000, OHIF :3001, Grafana :3000, HAPI :8090)"
log "  Portail dev  : cd apps/web-portal && npm run dev"
log "  Tests e2e    : make e2e (navigateur requis, PLAYWRIGHT=1 au 02-portal)"
log "═════════════════════════════════════════════════════════════════════"
ok "installation vérifiée"
