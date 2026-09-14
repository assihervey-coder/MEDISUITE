# Architecture du AI Model Mesh

## Principe : Capability Routing

Le système ne demande jamais « quel est mon meilleur LLM ? » mais
« quelle capacité dois-je mobiliser pour cette étape clinique ? ».

    CAPABILITY → MODEL REGISTRY → MODEL ROUTER → BEST AVAILABLE MODEL

## Registre (10 modèles, invariants vérifiés)

| Capacité | Modèle | Gateway | VRAM | Rôle |
|---|---|---|---|---|
| clinical_reasoning | Med42 v2 70B | ollama | 42 Go | synthèse encadrée |
| biomedical_synthesis | OpenBioLLM 70B | ollama | 42 Go | littérature/dossiers |
| logical_audit | DeepSeek-R1-Distill 32B | ollama | 20 Go | audit (jamais décideur) |
| image_analysis | MedGemma 4B IT | ollama | 4 Go | analyse contextualisée |
| image_triage | MiniCPM-V 2.6 | ollama | 6 Go | screening |
| image_segmentation | SAM2-Medical | vllm | 8 Go | masques/mesures |
| speech_dictation | MedASR quantifié | ollama | 1 Go | dictée FR/EN |
| conversation_transcription | Whisper Large v3 | ollama | 3 Go | multilingue terrain |
| embeddings | BGE-M3 | déterministe* | — | sensory retrieval |
| reranking | Qwen Reranker | déterministe* | — | top30→top5 |

*V1 : implémentations déterministes (hashing 256d / lexical autorité-pondéré) —
reproductibilité absolue ; les gateways Ollama/vLLM sont prêtes pour BGE-M3/Qwen.

## Invariants du registre

- `autonomous_diagnosis: false` — PARTOUT (vérifié par script + CI)
- `evidence_required: true` pour toute tâche clinique texte
- fallbacks déclarés (MiniCPM→MedGemma, chain local→server→déterministe)
- circuit breaker 3 échecs → down 5 min, puis re-test

## Rôles stricts (MARGE-inspired)

- L'agent conversationnel ne produit jamais de diagnostic de sa propre autorité
- MedGemma observe et décrit — le différentiel reste déterministe
- DeepSeek-R1 audite (cohérence, contradiction, coverage) — ne crée rien
- Un agent peut échouer : le pipeline déterministe continue toujours
