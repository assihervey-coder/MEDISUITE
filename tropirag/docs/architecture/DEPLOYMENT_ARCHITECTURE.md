# Déploiement — 4 nœuds × 8 GPU × 48 Go (1,536 To VRAM)

## Allocation des pools

| Nœud | GPU | Services | VRAM utilisée |
|---|---|---|---|
| 1 | 1-6 | MedASR, Whisper, BGE-M3, Qwen, MedGemma, MiniCPM-V, vector DB | ~30 Go |
| 2 | 1-8 | Med42-70B (TP=4) + OpenBioLLM-70B (TP=4) | ~85 Go |
| 3 | 1-8 | répliques Med42 + OpenBioLLM (domaines de panne croisés) | ~85 Go |
| 4 | 1-4 | DeepSeek-R1-Distill-32B | ~22 Go |
| 4 | 5-8 | standby tiède (BGE, Whisper, MedGemma) + batch nocturne | réserve |

## Règles de dimensionnement

1. **Jamais de TP inter-nœuds** sans InfiniBand — chaque modèle entier sur un nœud.
2. **Répliques croisées** : perte d'un nœud = 50 % capacité raisonnement, jamais 0.
3. **Standby tiède** sur nœud 4 pour les services critiques du nœud 1 (bascule < 1 min).
4. DeepSeek-R1 full (671B) : ne tient pas dans un nœud (Q4 ≈ 380-400 Go) → distill-32B.
5. Énergie : ~3-4 kW/nœud, 12-16 kW au total — circuits dédiés.

## Modes de déploiement

- **Docker Compose** (fourni) : API + Ollama profil mesh + Postgres profil HA
- **Déterministe** : `TROPIRAG_INFERENCE_MODE=deterministic` — aucun GPU requis
- **Hors-ligne complet** : bundle (voir offline/) — airgap natif
