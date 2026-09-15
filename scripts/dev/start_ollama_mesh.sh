#!/usr/bin/env bash
# Mesh LLM local TropiRAG — activation mono-commande.
#
#   scripts/dev/start_ollama_mesh.sh [port]
#
# Comportement :
#   1. nœud LLM : utilise le binaire `ollama` s'il existe (`ollama serve`),
#      sinon le serveur Ollama SIMULÉ embarqué (tropirag/scripts/
#      mock_ollama_server.py — réponses déterministes ancrées sur les preuves
#      du prompt, aucun contenu clinique inventé) ;
#   2. attend GET /api/version ;
#   3. redémarre tropirag-service avec TROPIRAG_INFERENCE_MODE=ollama et
#      TROPIRAG_OLLAMA_URL=http://127.0.0.1:<port> (les variables d'env
#      déjà exportées par l'appelant restent prioritaires) ;
#   4. vérifie /api/v1/health (ai_mesh.mode=ollama) et /api/v1/inference/nodes.
#
# Retour au mode déterministe : TROPIRAG_INFERENCE_MODE=deterministic
# (le mesh tombe alors en repli, l'aide à la décision reste fonctionnelle).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PORT="${1:-11434}"
VENV_PY="$ROOT/../.venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="$(command -v python3)"

echo "— Mesh LLM local TropiRAG (port $PORT) —"

# 1. nœud Ollama (réel ou simulé)
if ! curl -sf -m 2 "http://127.0.0.1:$PORT/api/version" >/dev/null 2>&1; then
  mkdir -p "$ROOT/logs"
  if command -v ollama >/dev/null 2>&1; then
    echo "• ollama binaire détecté — démarrage de ollama serve"
    nohup ollama serve >"$ROOT/logs/ollama-node.log" 2>&1 &
  else
    echo "• ollama binaire absent — nœud simulé (mock déterministe embarqué)"
    nohup "$VENV_PY" "$ROOT/tropirag/scripts/mock_ollama_server.py" \
      --port "$PORT" >"$ROOT/logs/ollama-mock.log" 2>&1 &
  fi
  for _ in $(seq 1 20); do
    curl -sf -m 2 "http://127.0.0.1:$PORT/api/version" >/dev/null 2>&1 && break
    sleep 0.5
  done
fi
curl -sf -m 2 "http://127.0.0.1:$PORT/api/version" >/dev/null
echo "✓ nœud LLM joignable sur :$PORT ($(curl -sf -m 2 http://127.0.0.1:$PORT/api/version))"

# 2. redémarrage de tropirag-service avec le mesh activé
export TROPIRAG_INFERENCE_MODE="${TROPIRAG_INFERENCE_MODE:-ollama}"
export TROPIRAG_OLLAMA_URL="${TROPIRAG_OLLAMA_URL:-http://127.0.0.1:$PORT}"
OLD="$(pgrep -f 'uvicorn tropirag.api.app:app' || true)"
if [ -n "$OLD" ]; then kill $OLD 2>/dev/null || true; sleep 1; fi
PYTHONPATH="$ROOT/packages/medisuite-core:$ROOT/tropirag" \
  MEDISUITE_PORT=8304 TROPIRAG_ROOT="$ROOT/tropirag" \
  TROPIRAG_DB_PATH="$ROOT/data/tropirag.db" TROPIRAG_DATA_DIR="$ROOT/tropirag" \
  nohup "$VENV_PY" -m uvicorn tropirag.api.app:app --host 0.0.0.0 --port 8304 \
  --log-level warning >"$ROOT/logs/tropirag-service.log" 2>&1 &
sleep 2

# 3. vérifications
HEALTH="$(curl -sf -m 5 http://127.0.0.1:8304/api/v1/health)"
echo "$HEALTH" | grep -q '"mode":"ollama"' \
  && echo "✓ health : ai_mesh.mode=ollama" \
  || { echo "✗ health inattendue : $HEALTH"; exit 1; }
curl -sf -m 5 http://127.0.0.1:8304/api/v1/inference/nodes \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
for url, v in r.get('nodes', {}).items():
    state = 'joignable' if v.get('reachable') else 'KO'
    print(f\"✓ nœud mesh {url} → {state} (v{v.get('version')}, {v.get('models')} modèles, {v.get('latency_ms')} ms)\")
print('mode inférence :', r.get('inference_mode'))
missing = r.get('missing_pulls') or {}
print('models manquants :', ', '.join(missing) if missing else 'aucun')
"
echo "✓ mesh LLM local ACTIF — synthèse IA encadrée par le Safety Gate"
