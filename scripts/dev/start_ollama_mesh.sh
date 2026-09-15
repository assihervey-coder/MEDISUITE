#!/usr/bin/env bash
# Mesh LLM local TropiRAG — activation mono-commande (mono-nœud ou multi-nœuds GPU).
#
#   scripts/dev/start_ollama_mesh.sh [port]          # mono-nœud (défaut)
#   scripts/dev/start_ollama_mesh.sh --multi         # topologie nodes.yaml (4 nœuds)
#
# Comportement :
#   1. nœuds LLM : utilise le binaire `ollama` s'il existe (un serveur par
#      nœud via OLLAMA_HOST/OLLAMA_MODELS dédiés), sinon des serveurs Ollama
#      SIMULÉS embarqués (tropirag/scripts/mock_ollama_server.py — réponses
#      déterministes ancrées sur les preuves du prompt, aucun contenu clinique
#      inventé) ;
#   2. attend GET /api/version sur chaque nœud ;
#   3. redémarre tropirag-service avec TROPIRAG_INFERENCE_MODE=ollama et
#      TROPIRAG_OLLAMA_URL + TROPIRAG_OLLAMA_NODES (routage par famille +
#      répliques croisées, cf. tropirag/deployment/ollama/nodes.yaml — les
#      variables déjà exportées par l'appelant restent prioritaires) ;
#   4. vérifie /api/v1/health (ai_mesh.mode=ollama) et /api/v1/inference/nodes
#      (tous les nœuds joignables).
#
# Topologie multi-nœuds (V1.1 — 4 nœuds × 8 GPU × 48 Go, AUCUN TP inter-nœuds) :
#   node1 :11434  input-evidence  speech/vision/embeddings/reranking
#   node2 :11435  reasoning-a     text (med42-v2-70b, openbiollm-70b)
#   node3 :11436  reasoning-b     text — réplique de node2
#   node4 :11437  audit-standby   auditeur (deepseek-r1-distill-32b)
#
# Retour au mode déterministe : TROPIRAG_INFERENCE_MODE=deterministic
# (le mesh tombe alors en repli, l'aide à la décision reste fonctionnelle).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PY="$ROOT/../.venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="$(command -v python3)"
MULTI=0
if [ "${1:-}" = "--multi" ]; then MULTI=1; PORT=11434; else PORT="${1:-11434}"; fi

NODE_LOG="$ROOT/logs/ollama-node.log"

# start_node <port> <models csv> <label>  → démarre un nœud s'il est absent
start_node() {
  local port="$1" models="$2" label="$3"
  if curl -sf -m 2 "http://127.0.0.1:$port/api/version" >/dev/null 2>&1; then
    echo "✓ $label :$port déjà joignable"
    return 0
  fi
  mkdir -p "$ROOT/logs" "$ROOT/data/ollama-node$port"
  if command -v ollama >/dev/null 2>&1; then
    echo "• $label :$port — ollama serve (GPU) — pull requis : $models"
    OLLAMA_HOST="127.0.0.1:$port" OLLAMA_MODELS="$ROOT/data/ollama-node$port" \
      nohup ollama serve >"$NODE_LOG" 2>&1 &
  else
    echo "• $label :$port — nœud simulé (mock déterministe embarqué)"
    nohup "$VENV_PY" "$ROOT/tropirag/scripts/mock_ollama_server.py" \
      --port "$port" --models "$models" >"$ROOT/logs/ollama-mock-$port.log" 2>&1 &
  fi
  for _ in $(seq 1 20); do
    curl -sf -m 2 "http://127.0.0.1:$port/api/version" >/dev/null 2>&1 && return 0
    sleep 0.5
  done
  echo "✗ $label :$port injoignable après 10 s (logs : $NODE_LOG)"; return 1
}

# ---------------------------------------------------------------------------
if [ "$MULTI" -eq 1 ]; then
  echo "— Mesh LLM local TropiRAG MULTI-NŒUDS (topologie deployment/ollama/nodes.yaml) —"
  # node1 : entrée + evidence (léger, haute cadence)
  start_node 11434 "medasr-quantized,whisper-large-v3,bge-m3,qwen-reranker,medgemma-4b-it,minicpm-v-2.6" "node1 input-evidence"
  # node2 : raisonnement lourd (text)
  start_node 11435 "med42-v2-70b,openbiollm-70b" "node2 reasoning-a"
  # node3 : réplique B du raisonnement (domaine de panne distinct)
  start_node 11436 "med42-v2-70b,openbiollm-70b" "node3 reasoning-b (réplique)"
  # node4 : audit + secours
  start_node 11437 "deepseek-r1-distill-32b" "node4 audit-standby"

  # Routage famille → nœud + répliques croisées (consommé par OllamaGateway.from_env)
  export TROPIRAG_INFERENCE_MODE="${TROPIRAG_INFERENCE_MODE:-ollama}"
  export TROPIRAG_OLLAMA_URL="${TROPIRAG_OLLAMA_URL:-http://127.0.0.1:11435}"
  export TROPIRAG_OLLAMA_NODES="${TROPIRAG_OLLAMA_NODES:-speech=http://127.0.0.1:11434,vision=http://127.0.0.1:11434,embeddings=http://127.0.0.1:11434,reranking=http://127.0.0.1:11434,text=http://127.0.0.1:11435,replicas=http://127.0.0.1:11436|http://127.0.0.1:11437}"
else
  echo "— Mesh LLM local TropiRAG (mono-nœud, port $PORT) —"
  start_node "$PORT" "med42-v2-70b,openbiollm-70b,deepseek-r1-distill-32b,medgemma-4b-it,minicpm-v-2.6,medasr-quantized,whisper-large-v3,bge-m3,qwen-reranker" "nœud LLM"
  export TROPIRAG_INFERENCE_MODE="${TROPIRAG_INFERENCE_MODE:-ollama}"
  export TROPIRAG_OLLAMA_URL="${TROPIRAG_OLLAMA_URL:-http://127.0.0.1:$PORT}"
  export TROPIRAG_OLLAMA_NODES="${TROPIRAG_OLLAMA_NODES:-}"
fi
echo "TROPIRAG_OLLAMA_URL=$TROPIRAG_OLLAMA_URL"
[ -n "${TROPIRAG_OLLAMA_NODES:-}" ] && echo "TROPIRAG_OLLAMA_NODES=$TROPIRAG_OLLAMA_NODES"

# ---------------------------------------------------------------------------
# Redémarrage de tropirag-service avec le mesh activé
OLD="$(pgrep -f 'uvicorn tropirag.api.app:app' || true)"
if [ -n "$OLD" ]; then kill $OLD 2>/dev/null || true; sleep 1; fi
PYTHONPATH="$ROOT/packages/medisuite-core:$ROOT/tropirag" \
  MEDISUITE_PORT=8304 TROPIRAG_ROOT="$ROOT/tropirag" \
  TROPIRAG_DB_PATH="$ROOT/data/tropirag.db" TROPIRAG_DATA_DIR="$ROOT/tropirag" \
  nohup "$VENV_PY" -m uvicorn tropirag.api.app:app --host 0.0.0.0 --port 8304 \
  --log-level warning >"$ROOT/logs/tropirag-service.log" 2>&1 &
sleep 2

# Vérifications
HEALTH="$(curl -sf -m 5 http://127.0.0.1:8304/api/v1/health)"
echo "$HEALTH" | grep -q '"mode":"ollama"' \
  && echo "✓ health : ai_mesh.mode=ollama" \
  || { echo "✗ health inattendue : $HEALTH"; exit 1; }
curl -sf -m 5 http://127.0.0.1:8304/api/v1/inference/nodes \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
nodes = r.get('nodes', {})
up = sum(1 for v in nodes.values() if v.get('reachable'))
for url, v in nodes.items():
    state = 'joignable' if v.get('reachable') else 'KO'
    print(f\"✓ nœud mesh {url} → {state} (v{v.get('version')}, {v.get('models')} modèles, {v.get('latency_ms')} ms)\")
print(f'nœuds : {up}/{len(nodes)} joignables — routage familles :', json.dumps(r.get('family_routing', {})))
print('répliques :', ', '.join(r.get('replicas', [])) or 'aucune')
print('mode inférence :', r.get('inference_mode'))
missing = r.get('missing_pulls') or {}
print('models manquants :', ', '.join(missing) if missing else 'aucun')
sys.exit(0 if up == len(nodes) and nodes else 1)
"
echo "✓ mesh LLM local ACTIF — synthèse IA encadrée par le Safety Gate"
