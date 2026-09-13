#!/usr/bin/env bash
# 02-portal — dépendances Node du portail clinique (apps/web-portal).
# Idempotent : npm ci rejoué seulement si node_modules est absent.
# PLAYWRIGHT=1 pour installer aussi le navigateur Chromium des tests e2e.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

PORTAL="${MEDISUITE_ROOT}/apps/web-portal"
need_cmd node npm

if [ ! -d "${PORTAL}/node_modules" ]; then
  log "installation des dépendances du portail (npm ci, lockfile versionné)"
  (cd "${PORTAL}" && (npm ci --no-audit --no-fund || npm install --no-audit --no-fund))
else
  ok "node_modules déjà présent — npm ci sauté (supprimer apps/web-portal/node_modules pour forcer)"
fi

[ -x "${PORTAL}/node_modules/.bin/vite" ] || die "vite introuvable après npm ci — vérifier package-lock.json"

if [ "${PLAYWRIGHT:-0}" = "1" ]; then
  log "installation du navigateur Chromium pour les tests e2e (playwright)"
  (cd "${PORTAL}" && npx playwright install --with-deps chromium) \
    || warn "chromium non installé — les parcours e2e (make e2e) nécessiteront un navigateur"
else
  warn "PLAYWRIGHT=1 non défini : navigateur e2e non installé (make e2e le demandera)"
fi

ok "portail prêt (vite présent) — poursuivre avec 03-env.sh"
