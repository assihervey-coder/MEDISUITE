#!/usr/bin/env bash
# (Re)démarre l'api-gateway (:8000) en arrière-plan robuste.
# Usage : scripts/dev/restart_gateway.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PY="$ROOT/../.venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="$(command -v python3)"

OLD="$(pgrep -f 'uvicorn src.main:app --host 0.0.0.0 --port 8000' || true)"
if [ -n "$OLD" ]; then kill $OLD 2>/dev/null || true; sleep 1; fi

PYTHONPATH="$ROOT/packages/medisuite-core:$ROOT/services/api-gateway" \
  nohup "$VENV_PY" -m uvicorn src.main:app --host 0.0.0.0 --port 8000 \
  --log-level warning >"$ROOT/logs/api-gateway.log" 2>&1 &

for _ in $(seq 1 20); do
  curl -sf -m 2 http://127.0.0.1:8000/health >/dev/null 2>&1 && break
  sleep 0.5
done
curl -sf -m 5 http://127.0.0.1:8000/health >/dev/null
echo "✓ api-gateway :8000 (routes /api/{service}/… — dont tropirag :8304)"
