# Branchement réel d'Ollama — 4 nœuds × 8 GPU × 48 Go

Guide opérationnel pour activer le **mesh IA complet** de TropiRAG sur
l'infrastructure locale (aucune dépendance cloud). Le mode déterministe
continue de fonctionner en parallèle et reste l'autorité de secours.

## 1. Topologie (figée avec l'architecture validée)

| Nœud | Rôle | Modèles résidents | GPU |
|---|---|---|---|
| **node1** | Entrée + Evidence | MedASR, Whisper Large v3, BGE-M3, Qwen Reranker, MedGemma-4B, MiniCPM-V | ~30 Go / 384 |
| **node2** | Raisonnement A | Med42-70B (TP=4), OpenBioLLM-70B (TP=4) | ~84 Go |
| **node3** | Raisonnement B (réplique) | Med42-70B (TP=4), OpenBioLLM-70B (TP=4) | ~84 Go |
| **node4** | Audit + secours | DeepSeek-R1-Distill-32B + batch nocturne | ~20 Go |

**Règle d'or** : aucun tenseur-parallelisme inter-nœuds (pas d'InfiniBand) ;
la réplication node2↔node3 est croisée sur des domaines de panne distincts.

## 2. Installation par nœud (une fois)

```bash
# sur chaque nœud (root ou sudo)
git clone https://github.com/assihervey-coder/TropiRAG.git
cd TropiRAG/deployment/ollama

./setup_node.sh 1    # node1 : entrée + evidence
./setup_node.sh 2    # node2 : raisonnement A
./setup_node.sh 3    # node3 : réplique
./setup_node.sh 4    # node4 : audit + secours
```

Le script installe Ollama, configure le service systemd (écoute `0.0.0.0:11434`),
télécharge les modèles du nœud et applique les **Modelfiles** (prompts système
cliniques TropiRAG : citations obligatoires, zéro posologie, jamais de diagnostic).

## 3. Vérification du mesh

```bash
# depuis le bastion (voire n'importe quel nœud)
./health_check.sh
```

Sortie attendue : 4 nœuds `✓` avec version Ollama + modèles résidents,
puis un test de génération Med42 sur node2.

## 4. Bascule de l'API en mode Ollama

```bash
export TROPIRAG_INFERENCE_MODE=ollama
export TROPIRAG_OLLAMA_URL="http://node2.tropirag.local:11434"
export TROPIRAG_OLLAMA_NODES="speech=http://node1.tropirag.local:11434,vision=http://node1.tropirag.local:11434,embeddings=http://node1.tropirag.local:11434,reranking=http://node1.tropirag.local:11434,text=http://node2.tropirag.local:11434"

uvicorn tropirag.api.app:app --host 0.0.0.0 --port 8000
# ou : ./switch_to_ollama.sh   (guide interactif)
```

La gateway Ollama route chaque requête **modèle → famille → nœud**, avec repli
automatique sur node3 (réplique) puis sur la gateway déterministe — le pipeline
ne s'arrête jamais.

Vérifier l'état réel : `curl http://localhost:8000/api/v1/inference/nodes`
→ santé par nœud, routage familles, modèles manquants + commandes `ollama pull`.

## 5. Ce qui change / ne change PAS

| Élément | En mode déterministe | En mode Ollama |
|---|---|---|
| Règles, red flags, escalades | ✅ identiques | ✅ identiques |
| Contre-indications médicamenteuses | ✅ identiques | ✅ identiques |
| Citations RAG | BM25 + vecteurs hashing | + BGE-M3 réel + Qwen reranker |
| Synthèse narrative | gabarits structurés | Med42/OpenBioLLM (sous guards) |
| Dictée / photo mobile | repli local | MedASR/Whisper + MedGemma |
| **Safety Gate (7 invariants)** | **toujours actif** | **toujours actif** |

## 6. Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `INJOIGNABLE` sur un nœud | service arrêté / pare-feu | `systemctl status ollama` ; ouvrir 11434 |
| `ollama pull` échoue (node2/3, 70B) | disque < 45 Go libres | `df -h` ; nettoyer `/usr/share/ollama` |
| Génération lente node2 | TP non actif | vérifier `OLLAMA_NUM_PARALLEL`, `nvidia-smi` |
| `404 model not found` | modèle non pullé | l'API renvoie la commande `ollama pull …` |
| node2 HS | panne matérielle | rien à faire : bascule auto node3 → déterministe |

## 7. Contenu du dossier

```
deployment/ollama/
├── nodes.yaml            # topologie + routage familles (source de vérité)
├── setup_node.sh         # installation complète d'un nœud
├── pull_models.sh        # téléchargement des modèles par nœud
├── apply_modelfiles.sh   # application des prompts système cliniques
├── health_check.sh       # santé mesh (--local pour un seul nœud)
├── switch_to_ollama.sh   # guide de bascule du mode API
└── Modelfiles/           # 9 Modelfiles (prompts TropiRAG alignés src/tropirag/ai/prompts)
```
