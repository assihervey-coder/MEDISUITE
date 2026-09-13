#!/usr/bin/env bash
# Injecte les données de démonstration ivoiriennes dans tous les services.
set -e
echo "Les seeds sont automatiques au premier appel de chaque API (déterministes, seed=42)."
echo "Exemple : curl -s localhost:8002/api/v1/patients | head -c 400"
