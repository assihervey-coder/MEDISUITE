#!/usr/bin/env bash
# TropiRAG V1.1 — Application des Modelfiles (prompts système cliniques).
# Usage : ./apply_modelfiles.sh <1|2|3|4>   (à exécuter sur le nœud concerné)
set -euo pipefail

NODE="${1:-}"
MODELS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/Modelfiles"

if [[ -z "$NODE" || ! -d "$MODELS_DIR" ]]; then
  echo "Usage : $0 <1|2|3|4> — Modelfiles requis dans $MODELS_DIR"
  exit 1
fi

# Modelfiles applicables par nœud
for_node() {
  case "$1" in
    1) echo "medasr-quantized whisper-large-v3 bge-m3 qwen-reranker medgemma-4b-it minicpm-v-2.6";;
    2) echo "med42-v2-70b openbiollm-70b";;
    3) echo "med42-v2-70b openbiollm-70b";;
    4) echo "deepseek-r1-distill-32b";;
  esac
}

for model in $(for_node "$NODE"); do
  mf="$MODELS_DIR/${model}.Modelfile"
  if [[ -f "$mf" ]]; then
    echo "◆ Création du modèle spécialisé : ${model} (tropirag/${model})"
    ollama create "tropirag/${model}" -f "$mf"
  else
    echo "! Modelfile absent pour ${model} — modèle brut utilisé"
  fi
done
echo "✓ Modelfiles appliqués — 'ollama list' pour vérifier les tags tropirag/*"
