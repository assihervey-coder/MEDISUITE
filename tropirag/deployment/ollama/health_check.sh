#!/usr/bin/env bash
# TropiRAG V1.1 — Santé des nœuds Ollama du mesh.
# Usage :
#   ./health_check.sh              # vérifie les 4 nœuds (depuis le bastion/API)
#   ./health_check.sh --local      # vérifie uniquement ce nœud
set -euo pipefail

LOCAL_ONLY="${1:-}"

GREEN="✓"; RED="✗"; YEL="!"

check_node() {
  local name="$1" url="$2" expect="$3"
  local version models_ok=""
  version=$(curl -sS --max-time 3 "${url}/api/version" 2>/dev/null | sed -n 's/.*"version":"\([^"]*\)".*/\1/p' || true)
  if [[ -z "$version" ]]; then
    printf "%s %-8s %-38s %s\n" "$RED" "$name" "$url" "INJOIGNABLE"
    return 1
  fi
  # modèles présents ?
  local tags
  tags=$(curl -sS --max-time 5 "${url}/api/tags" 2>/dev/null || echo "{}")
  local count
  count=$(echo "$tags" | grep -o '"name"' | wc -l | tr -d ' ')
  printf "%s %-8s %-38s v%-6s %s modèles\n" "$GREEN" "$name" "$url" "$version" "$count"
  # vérification des modèles attendus
  if [[ -n "$expect" ]]; then
    for m in $expect; do
      if echo "$tags" | grep -q "\"name\":\"${m}[:\"]"; then
        printf "    %s %s\n" "$GREEN" "$m"
      else
        printf "    %s %s  →  ollama pull %s\n" "$RED" "$m" "$m"
      fi
    done
  fi
}

echo "═══════════ TropiRAG — santé du mesh Ollama ═══════════"

if [[ "$LOCAL_ONLY" == "--local" ]]; then
  check_node "local" "http://localhost:11434" \
    "$(case "${TROPIRAG_THIS_NODE:-1}" in
        1) echo "medasr-quantized whisper-large-v3 bge-m3 qwen-reranker medgemma-4b-it minicpm-v-2.6";;
        2|3) echo "med42-v2-70b openbiollm-70b";;
        4) echo "deepseek-r1-distill-32b";;
      esac)"
  exit 0
fi

check_node "node1" "${TROPIRAG_NODE1:-http://node1.tropirag.local:11434}" \
  "medasr-quantized whisper-large-v3 bge-m3 qwen-reranker medgemma-4b-it minicpm-v-2.6"
check_node "node2" "${TROPIRAG_NODE2:-http://node2.tropirag.local:11434}" \
  "med42-v2-70b openbiollm-70b"
check_node "node3" "${TROPIRAG_NODE3:-http://node3.tropirag.local:11434}" \
  "med42-v2-70b openbiollm-70b"
check_node "node4" "${TROPIRAG_NODE4:-http://node4.tropirag.local:11434}" \
  "deepseek-r1-distill-32b"

echo ""
echo "── Test de génération (node2, Med42) ──"
curl -sS --max-time 20 "${TROPIRAG_NODE2:-http://node2.tropirag.local:11434}/api/generate" \
  -d '{"model":"med42-v2-70b","prompt":"Say OK","stream":false}' \
  | sed -n 's/.*"response":"\([^"]*\)".*/réponse : \1/p' \
  || echo "✗ génération échouée — vérifier VRAM (nvidia-smi) et les logs (journalctl -u ollama)"
