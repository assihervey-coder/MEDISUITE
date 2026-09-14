# Architecture RAG

    QUERY → [BM25 ∥ VECTOR(hashing 256d)] → TOP 30 → FUSION RRF(k=60)
          → RERANK (lexical autorité-pondéré | Qwen si mesh) → TOP 5
          → VALIDATION (source, temporalité) → EVIDENCE PACK

## Corpus embarqué (27 unités, 17 sources)

- Autorités : OMS (22), MSF (3), CDC (1), MSP Côte d'Ivoire (1)
- Chaque unité : passage autonome citable + section + juridiction + dates
- Manifeste d'intégrité SHA-256 (corpus/manifests/)

## Politique de preuve

1. Hiérarchie d'autorité : WHO > national/MSF/CDC > institutional > scientific
2. Unités périmées (valid_until) exclues du pack actif — jamais supprimées
3. Conflits détectés (contradiction_detector) → résolution par rang
4. Boost de rerank par autorité : WHO ×1.15, national/MSF/CDC ×1.10

## Pourquoi hashing déterministe en V1

Le hashing 256d rend le retrieval **bit-identique entre machines** — un critère
d'auditabilité et de revalidation clinique. BGE-M3 s'active par gateway quand
le mesh est prêt ; l'interface (VectorIndex.build(embed_fn)) est déjà branchée.
