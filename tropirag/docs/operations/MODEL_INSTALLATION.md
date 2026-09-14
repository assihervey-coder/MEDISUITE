# Installation des modèles du mesh (optionnel)

TropiRAG fonctionne **entièrement sans modèle** (mode déterministe).
Le mesh s'active en trois étapes sur les nœuds GPU :

## 1. Ollama + Modelfiles

```bash
# sur chaque nœud concerné
curl -fsSL https://ollama.com/install.sh | sh
ollama create med42 -f deployment/ollama/Modelfiles/med42/Modelfile
ollama create openbiollm -f deployment/ollama/Modelfiles/openbiollm/Modelfile
ollama create deepseek-r1 -f deployment/ollama/Modelfiles/deepseek/Modelfile
ollama pull medgemma:4b-it
ollama pull minicpm-v:latest
```

## 2. Vérifier la santé du mesh

```bash
python scripts/benchmark_models.py   # disponibilité modèle par modèle
python scripts/validate_models.py    # invariants du registre
```

## 3. Activer

```bash
export TROPIRAG_INFERENCE_MODE=ollama
make api
```

Le routeur bascule chaque capacité vers son modèle ; en cas d'indisponibilité,
repli déterministe automatique (jamais de silence).
