# MEDISUITE — bibliothèque partagée des scripts de setup local (v0.13).
# Sourcing obligatoire : source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
# Convention : chaque script NN-*.sh est IDEMPOTENT (ré-exécutable sans
# dommage), verbeux sur ce qu'il fait, honnête sur ce qu'il saute (🟠).
# shellcheck shell=bash

set -euo pipefail

# Racine du dépôt = deux niveaux au-dessus de local-deployment/setup/.
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
MEDISUITE_ROOT="$(cd "${SETUP_DIR}/../.." && pwd)"

if [ -t 1 ] && [ "${TERM:-}" != "dumb" ]; then
  C_G="\033[32m"; C_O="\033[33m"; C_R="\033[31m"; C_B="\033[36m"; C_0="\033[0m"
else
  C_G=""; C_O=""; C_R=""; C_B=""; C_0=""
fi

_step="${0##*/}"

log()  { printf "${C_B}[setup] [${_step}]${C_0} %s\n" "$*"; }
ok()   { printf "${C_G}[setup] [${_step}] 🟢${C_0} %s\n" "$*"; }
warn() { printf "${C_O}[setup] [${_step}] 🟠${C_0} %s\n" "$*"; }
die()  { printf "${C_R}[setup] [${_step}] 🔴${C_0} %s\n" "$*" >&2; exit 1; }

# need_cmd <cmd>… — s'arrête au premier absent avec un message actionnable.
need_cmd() {
  local c
  for c in "$@"; do
    command -v "$c" >/dev/null 2>&1 || die "outil requis absent : ${c} — installer puis relancer"
  done
}

# has_cmd <cmd> — vrai/faux sans arrêt (pour les étapes optionnelles).
has_cmd() { command -v "$1" >/dev/null 2>&1; }

# wait_http <url> <timeout_s> <msg> — boucle curl jusqu'à 200/3xx.
wait_http() {
  local url="$1" timeout="${2:-120}" msg="${3:-$url}" i=0
  log "attente de ${msg} (${url}, max ${timeout}s)…"
  while [ "$i" -lt "$timeout" ]; do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then ok "prêt : ${msg}"; return 0; fi
    sleep 2; i=$((i + 2))
  done
  warn "timeout en attendant ${msg} (${url}) — vérifier les logs du conteneur"
  return 1
}

# docker_ready — 0 si le démon docker répond (sinon 1, sans tuer le script).
docker_ready() { has_cmd docker && docker info >/dev/null 2>&1; }

# venved <cmd>… — exécute une commande avec la venv du dépôt en tête de PATH.
venved() {
  local venv="${MEDISUITE_ROOT}/.venv"
  [ -x "${venv}/bin/python" ] || die "venv absente (${venv}) — exécuter 01-python.sh"
  PATH="${venv}/bin:${PATH}" "$@"
}

# compose_file — chemin unique de la stack minimale.
COMPOSE_FILE="${MEDISUITE_ROOT}/local-deployment/docker-compose.minimal.yml"
