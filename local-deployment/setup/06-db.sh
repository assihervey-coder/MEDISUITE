#!/usr/bin/env bash
# 06-db — initialisation des bases SQLite + seeds de démonstration (mode natif).
# Démarre les 38 services, exécute le smoke, puis les arrête : les fichiers
# SQLite (data/*.sqlite3) sont prêts pour un `make dev-up` instantané.
# Idempotent : les seeds des services sont protégés contre la duplication.
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"

if [ "${SKIP_SEED:-0}" = "1" ]; then
  warn "SKIP_SEED=1 : initialisation des bases sautée 🟠"
  exit 0
fi

log "démarrage éphémère des services (run_all --up) pour créer + peupler les bases"
venved python3 "${MEDISUITE_ROOT}/services/run_all.py" --up

log "pause de démarrage (5 s) puis smoke test"
sleep 5
venved python3 "${MEDISUITE_ROOT}/services/smoke_test.py" \
  || warn "smoke incomplet — certains services n'ont pas répondu (voir ci-dessus) 🟠"

log "arrêt des services (run_all --down) — les bases restent sur disque"
venved python3 "${MEDISUITE_ROOT}/services/run_all.py" --down

ok "bases SQLite initialisées + seeds chargés — poursuivre avec 07-images.sh (docker) ou 10-verify.sh (natif)"
