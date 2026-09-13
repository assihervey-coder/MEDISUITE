ROOT_DIR   := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY         ?= python3
PIP        := $(PY) -m pip install --break-system-packages -q

.PHONY: help install install-core test test-rules test-services test-ai test-tools model-cards dev-up dev-down smoke tree stats

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Installe toutes les dépendances Python
	$(PIP) -r requirements.txt
	$(PIP) -r ai/requirements-dev.txt

install-core: ## Dépendances minimales (tests rapides)
	$(PIP) fastapi uvicorn sqlalchemy httpx pytest pyyaml numpy

test: test-rules test-services test-ai test-tools ## Tous les tests

test-rules: ## Moteur de règles cliniques (le plus important)
	cd packages/clinical-rules && $(PY) -m pytest tests/ -q

test-services: ## Tests de tous les microservices
	$(PY) services/run_tests.py

test-ai: ## Tests fusion multimodale
	cd ai && $(PY) -m pytest multimodal/tests/ -q

test-tools: ## Outils transverses (model-cards, audit, comparaison)
	$(PY) -m pytest tools/tests/ -q

model-cards: ## Régénère les 26 model-cards MDR (puis recommittre)
	$(PY) tools/generate_model_cards.py && $(PY) tools/generate_model_cards.py --check

e2e: ## Parcours e2e Playwright du portal (APIs mockées)
	cd apps/web-portal && npx playwright test

dev-up: ## Démarre les services en local (ports 8000+)
	$(PY) services/run_all.py --up

dev-down: ## Arrête tous les services
	$(PY) services/run_all.py --down

smoke: ## Smoke test : santé de tous les services
	$(PY) services/smoke_test.py

tree: ## Affiche l'arborescence
	$(PY) scripts/dev/tree.py

stats: ## Statistiques du code
	@echo "Fichiers Python : $$(find . -name '*.py' -not -path './.git/*' | wc -l)"
	@echo "Lignes Python   : $$(find . -name '*.py' -not -path './.git/*' -exec cat {} + | wc -l)"
	@echo "Fichiers TS/TSX : $$(find . \( -name '*.ts' -o -name '*.tsx' \) -not -path './.git/*' | wc -l)"
