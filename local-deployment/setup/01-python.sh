#!/usr/bin/env bash
# 01-python — venv du dépôt + dépendances Python du socle.
# Idempotent : la venv est créée une seule fois, pip réinstalle sans dommage.
# SKIP_AI=1 pour sauter ai/requirements-dev.txt (torch, lourd) — l'IA n'est
# pas requise pour faire tourner les 38 services ni le portal.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

need_cmd python3
VENV="${MEDISUITE_ROOT}/.venv"

if [ ! -x "${VENV}/bin/python" ]; then
  log "création de la venv : ${VENV}"
  python3 -m venv "${VENV}"
else
  ok "venv déjà présente : ${VENV}"
fi

log "mise à jour de pip/wheel dans la venv"
"${VENV}/bin/pip" install -q --upgrade pip wheel

log "installation des dépendances socle (requirements.txt)"
"${VENV}/bin/pip" install -q -r "${MEDISUITE_ROOT}/requirements.txt"

if [ "${SKIP_AI:-0}" = "1" ]; then
  warn "SKIP_AI=1 : ai/requirements-dev.txt ignoré (torch/monai non installés)"
elif [ -f "${MEDISUITE_ROOT}/ai/requirements-dev.txt" ]; then
  log "installation des dépendances IA (torch/monai — plusieurs minutes)"
  "${VENV}/bin/pip" install -q -r "${MEDISUITE_ROOT}/ai/requirements-dev.txt" \
    || warn "dépendances IA non installées — les tests IA (make test-ai) seront indisponibles"
fi

log "vérification d'imports du socle"
"${VENV}/bin/python" - <<'EOF'
import fastapi, sqlalchemy, httpx, yaml, numpy  # noqa: F401
print("imports socle OK : fastapi, sqlalchemy, httpx, yaml, numpy")
EOF

ok "python prêt — poursuivre avec 02-portal.sh"
