#!/usr/bin/env bash
# TropiRAG V1.1 — Installation d'un nœud Ollama (à exécuter sur CHAQUE nœud GPU).
# Usage : ./setup_node.sh <1|2|3|4> [--hostname h]
set -euo pipefail

NODE="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/Modelfiles"

if [[ -z "$NODE" || ! "$NODE" =~ ^[1-4]$ ]]; then
  echo "Usage : $0 <numéro de nœud 1-4>"
  echo "  1 = entrée + evidence (ASR, Whisper, BGE-M3, Qwen, MedGemma, MiniCPM)"
  echo "  2 = raisonnement A (Med42-70B TP=4, OpenBioLLM-70B TP=4)"
  echo "  3 = raisonnement B — réplique (Med42-70B TP=4, OpenBioLLM-70B TP=4)"
  echo "  4 = audit + secours (DeepSeek-R1-Distill-32B, batch nocturne)"
  exit 1
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║   TropiRAG — installation nœud ${NODE} (4×8 GPU×48Go)        ║"
echo "╚══════════════════════════════════════════════════════╝"

# 1. Installation d'Ollama si absent ------------------------------------
if ! command -v ollama >/dev/null 2>&1; then
  echo "→ Installation d'Ollama…"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "✓ Ollama déjà installé : $(ollama --version 2>/dev/null || echo 'version inconnue')"
fi

# 2. Service systemd (persistant, écoute sur toutes les interfaces) ------
install -d /etc/systemd/system 2>/dev/null || true
if command -v systemctl >/dev/null 2>&1; then
  if [[ "$EUID" -eq 0 ]]; then
    systemctl enable --now ollama 2>/dev/null || true
    # écoute réseau : nécessaire pour le routage inter-nœuds
    mkdir -p /etc/systemd/system/ollama.service.d
    cat > /etc/systemd/system/ollama.service.d/override.conf <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
    systemctl daemon-reload
    systemctl restart ollama
    echo "✓ Service systemd configuré (OLLAMA_HOST=0.0.0.0:11434)"
  else
    echo "⚠ Exécuter en root pour le service systemd ; sinon lancer 'ollama serve' manuellement."
    export OLLAMA_HOST=0.0.0.0:11434
  fi
fi

# 3. Variables d'environnement Ollama (TP local uniquement) ---------------
case "$NODE" in
  2|3)
    # Med42/OpenBioLLM en TP=4 intra-nœud (4 GPU) — JAMAIS inter-nœuds
    export OLLAMA_NUM_PARALLEL=4
    ;;
  4)
    export OLLAMA_NUM_PARALLEL=4
    export OLLAMA_KEEP_ALIVE=24h   # l'auditeur reste résident
    ;;
esac

# 4. Téléchargement des modèles du nœud -----------------------------------
echo "→ Téléchargement des modèles du nœud ${NODE}…"
bash "$SCRIPT_DIR/pull_models.sh" "$NODE"

# 5. Modelfiles spécialisés (prompts système cliniques) ------------------
if [[ -d "$MODELS_DIR" ]]; then
  bash "$SCRIPT_DIR/apply_modelfiles.sh" "$NODE"
fi

# 6. Vérification ---------------------------------------------------------
echo "→ Vérification locale…"
sleep 2
bash "$SCRIPT_DIR/health_check.sh" --local

echo ""
echo "✅ Nœud ${NODE} prêt. Routage famille→URL à déclarer côté API :"
echo "   voir deployment/ollama/nodes.yaml (TROPIRAG_OLLAMA_NODES)"
