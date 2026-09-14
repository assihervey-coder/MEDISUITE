#!/usr/bin/env bash
# TropiRAG V1.1 — Bascule du serveur API en mode Ollama (mesh IA réel).
# Usage : ./switch_to_ollama.sh [URL_API] [URL_OLLAMA_DEFAUT]
#   Les nœuds par famille se configurent via TROPIRAG_OLLAMA_NODES (voir nodes.yaml).
set -euo pipefail

API_URL="${1:-http://localhost:8000}"

echo "═══════ TropiRAG — passage en mode OLLAMA (mesh IA) ═══════"

# 1. Vérifier que les nœuds répondent
bash "$(dirname "$0")/health_check.sh" || {
  echo ""
  echo "✗ Des nœuds manquent. Continuer quand même ? (o/N)"
  read -r ans
  [[ "${ans:-n}" == "o" ]] || exit 1
}

# 2. Variables d'environnement du mesh (à exporter AVANT uvicorn)
cat <<'ENV'
── À exporter avant de (re)lancer l'API ──────────────────────────
export TROPIRAG_INFERENCE_MODE=ollama
export TROPIRAG_OLLAMA_URL="http://node2.tropirag.local:11434"
export TROPIRAG_OLLAMA_NODES="speech=http://node1.tropirag.local:11434,vision=http://node1.tropirag.local:11434,embeddings=http://node1.tropirag.local:11434,reranking=http://node1.tropirag.local:11434,text=http://node2.tropirag.local:11434"
# réplique node3 = repli automatique si node2 tombe (géré par la gateway)
ENV

echo ""
echo "3. Redémarrer l'API :"
echo "   systemctl restart tropirag   # ou :"
echo "   TROPIRAG_INFERENCE_MODE=ollama TROPIRAG_OLLAMA_NODES=… uvicorn tropirag.api.app:app"
echo ""
echo "4. Vérifier :"
echo "   curl $API_URL/api/v1/inference/nodes   → état des nœuds + pulls manquants"
echo "   curl $API_URL/api/v1/health           → mode=ollama"
