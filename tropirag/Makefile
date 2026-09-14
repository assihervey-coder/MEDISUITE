# TropiRAG — Makefile
PYTHON ?= python3
PIP ?= pip
export TROPIRAG_ROOT := $(abspath $(lastword $(MAKEFILE_LIST)))/..
ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

export PYTHONPATH := $(ROOT)/src
export TROPIRAG_DATA_DIR ?= $(ROOT)

.DEFAULT_GOAL := help

.PHONY: help setup diagnostics index demo api test unit integration clinical-safety validate-rules ingest commit

help:
	@echo "TropiRAG — commandes disponibles :"
	@echo "  make setup         installe les dépendances (pip -e .[dev])"
	@echo "  make diagnostics   diagnostic système complet (sans GPU)"
	@echo "  make ingest        ingère le corpus (evidence units) en base"
	@echo "  make index         construit les index BM25 + vectoriels"
	@echo "  make demo          exécute le cas fièvre+voyage en CLI"
	@echo "  make api           lance l'API + dashboard (uvicorn)"
	@echo "  make test          tous les tests"
	@echo "  make unit          tests unitaires uniquement"
	@echo "  make safety        tests de sécurité uniquement"
	@echo "  make validate-rules valide les règles YAML (lint clinique)"

setup:
	$(PIP) install -e ".[dev,api]"

diagnostics:
	$(PYTHON) scripts/system_diagnostics.py

ingest:
	$(PYTHON) scripts/ingest_corpus.py

index: ingest
	$(PYTHON) scripts/build_bm25_index.py
	$(PYTHON) scripts/build_vector_index.py

demo:
	$(PYTHON) scripts/run_case.py --scenario fever_travel_ci

api:
	$(PYTHON) -m uvicorn tropirag.api.app:app --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest tests

unit:
	$(PYTHON) -m pytest tests/unit -q

integration:
	$(PYTHON) -m pytest tests/integration -q

safety:
	$(PYTHON) -m pytest tests/safety tests/adversarial -q

validate-rules:
	$(PYTHON) scripts/validate_rules.py

benchmark:
	$(PYTHON) scripts/evaluate_rag.py
