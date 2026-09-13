# Architecture vivante

- `baseline/` — état actuel dérivé des sources de vérité (`services/registry.py`, `datasets/registry.py`, `ai/multimodal/configs/`, manifests k8s)
- `target/` — état cible de la prochaine baseline
- `dependency-graph/` — nœuds/arêtes des dépendances (consommé par impact-engine et test-impact-engine)
- `architecture-diff/` — générateurs, snapshots horodatés, rapports « que change exactement cette proposition ? »

Toute proposition approuvée produit un snapshot avant/après + diff signé dans `architecture-diff/reports/`.
