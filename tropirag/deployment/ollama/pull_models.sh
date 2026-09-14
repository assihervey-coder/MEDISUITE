#!/usr/bin/env bash
# TropiRAG V1.1 — Téléchargement des modèles Ollama pour un nœud donné.
# Usage : ./pull_models.sh <1|2|3|4>
set -euo pipefail

NODE="${1:-}"

models_for_node() {
  case "$1" in
    1) # entrée + evidence
      echo "medasr-quantized
whisper-large-v3
bge-m3
qwen-reranker
medgemma-4b-it
minicpm-v-2.6" ;;
    2) # raisonnement A
      echo "med42-v2-70b
openbiollm-70b" ;;
    3) # raisonnement B (réplique)
      echo "med42-v2-70b
openbiollm-70b" ;;
    4) # audit + secours
      echo "deepseek-r1-distill-32b" ;;
    *) return 1 ;;
  esac
}

if ! models_for_node "$NODE" >/dev/null 2>&1; then
  echo "Usage : $0 <1|2|3|4>"
  exit 1
fi

echo "── Téléchargement des modèles du nœud ${NODE} ──────────────"
TOTAL_GB=0
for model in $(models_for_node "$NODE"); do
  echo ""
  echo "◆ ollama pull ${model}"
  ollama pull "$model"
done

echo ""
echo "── Modèles résidents du nœud ────────────────────────────────"
ollama list
echo ""
echo "Astule VRAM : chaque modèle reste résident (OLLAMA_KEEP_ALIVE) ;"
echo "surveiller avec : watch -n 5 nvidia-smi"
