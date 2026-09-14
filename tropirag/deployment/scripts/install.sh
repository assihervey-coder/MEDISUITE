#!/usr/bin/env bash
# TropiRAG — installation locale (Linux)
set -e
cd "$(dirname "$0")/../.."
echo "── 1/4 dépendances Python"
python3 -m pip install -e ".[dev,api]"
echo "── 2/4 validation des règles cliniques"
python3 scripts/validate_rules.py
echo "── 3/4 construction des index RAG"
python3 scripts/ingest_corpus.py
python3 scripts/build_bm25_index.py
python3 scripts/build_vector_index.py
echo "── 4/4 diagnostic système"
python3 scripts/system_diagnostics.py
echo "✓ Installation terminée — make api pour lancer le serveur"
