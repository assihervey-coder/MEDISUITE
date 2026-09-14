# Installation

## Prérequis
- Python 3.11+
- (optionnel) Ollama pour le mesh IA — sinon tout fonctionne en déterministe

## Installation rapide

```bash
./deployment/scripts/install.sh
# ou manuellement :
pip install -e ".[dev,api]"
python scripts/validate_rules.py     # lint des 80+ règles cliniques
python scripts/system_diagnostics.py # 16 vérifications
```

## Lancer

```bash
make api            # API + dashboard → http://localhost:8000
make demo           # cas de démonstration en CLI
make test           # 120 tests
```

## Clé API

Copier `.env.example` → `.env` puis définir `TROPIRAG_API_KEY`.
Le dashboard la demande à la première requête (stockée localement).
