# Bundle hors-ligne TropiRAG (airgap)

## Contenu
- models/ : à remplir avec les GGUF/Ollama blobs (voir MODEL_INSTALLATION.md)
- corpus/ : corpus de preuves embarqué (déjà inclus dans le repo)
- installer/ : ce guide

## Installation en environnement isolé

1. Copier l'archive sur la machine cible.
2. `pip install -e ".[api]" --no-index --find-links wheels/` (fournir les wheels)
3. `TROPIRAG_INFERENCE_MODE=deterministic make api`
4. Le système fonctionne SANS réseau, SANS GPU — mode déterministe intégral.

## Activation du mesh en airgap
Pré-charger les modèles Ollama via `ollama pull` sur une machine connectée,
puis copier `/root/.ollama` vers les nœuds cibles.
