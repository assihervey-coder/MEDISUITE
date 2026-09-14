# Architecture système

    CAS CLINIQUE
        │
        ▼
    ┌──────────────────────┐   DÉTERMINISTE (autorité)
    │ ClinicalOrchestrator │   règles 83+ · red flags · escalade · temporel
    │  rules → safety →    │   différentiel pondéré · contraintes médicamenteuses
    │  temporal → diff.   │
    └─────────┬────────────┘
              ▼
    ┌──────────────────────┐
    │    Query Planner     │   requête de retrieval (symptômes+voyage+diff.)
    └─────────┬────────────┘
              ▼
    ┌──────────────────────┐   EVIDENCE (preuves sourcées)
    │   Evidence Engine    │   BM25 ∥ vecteurs (256d) → fusion RRF(60)
    │  rerank → validate   │   → rerank lexical autorité-pondéré → TOP 5
    └─────────┬────────────┘
              ▼
    ┌──────────────────────┐   AI MESH (sous garde)
    │  MedicalAgent/Med42  │   synthèse JSON citée (si risque le permet)
    │  ReasoningEngine/R1  │   audit cohérence/contradictions/coverage
    └─────────┬────────────┘
              ▼
    ┌──────────────────────┐   SAFETY GATE (décision finale)
    │  G1..G7 invariants   │   posologie ? diagnostic ? preuve ? gravité ?
    └─────────┬────────────┘
              ▼
    ┌──────────────────────┐
    │  Response Engine     │   narrative déterministe + citations + provenance
    └──────────────────────┘

## Topologie cible (4 nœuds × 8 GPU × 48 Go)

- NŒUD 1 : ASR, BGE-M3, Qwen Reranker, MedGemma, MiniCPM-V, vector DB
- NŒUD 2/3 : Med42-70B (TP=4) + OpenBioLLM-70B (TP=4), 2 répliques croisées
- NŒUD 4 : DeepSeek-R1-Distill-32B, standby, batch nocturne
- Règle : jamais de TP inter-nœuds sans InfiniBand.

Voir DEPLOYMENT_ARCHITECTURE.md pour l'allocation GPU complète.
