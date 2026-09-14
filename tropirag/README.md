# SIGH-CI — Système Intégré de Gestion Hospitalière de Côte d'Ivoire

[![Tests](https://img.shields.io/badge/Tests-358%2F358%20%E2%9C%93-brightgreen)](tests/)
[![Build](https://img.shields.io/badge/Build-passing-brightgreen)](Makefile)
[![Conformité](https://img.shields.io/badge/Conformit%C3%A9-Loi%20CI%20n%C2%B02013--450-blue)](docs/governance/)
[![Licence](https://img.shields.io/badge/Licence-Propri%C3%A9taire-red)](LICENSE)

> **Plateforme hospitalière ivoirienne conforme à la Loi CI n°2013-450**
> (protection des données personnelles), avec registre DPO, AIPD, PCA,
> backups chiffrés AES-256-GCM et monitoring Prometheus/Grafana/Sentry.

---

# TropiRAG V1.4 — Compagnon Clinique de Terrain

> **Fièvre + Voyage — Afrique de l'Ouest** · Architecture AI Model Mesh · Autorité clinique déterministe
> **Couverture de construction : 100 % sur les 8 domaines du plan** (voir tableau ci-dessous)

TropiRAG est une plateforme d'aide à la décision clinique pour les contextes
tropicaux (Côte d'Ivoire et sous-région), conçue autour d'un principe absolu :

```
IA ≠ autorité clinique

IA            → analyse / extraction / recherche / raisonnement / synthèse
Evidence      → sources authentifiées (OMS, MSF, CDC, national) + citations
Rule Engine   → suspicion, gravité, contraintes (déterministe)
Safety Gate   → red flags, escalade, refus (déterministe)
Réponse       → clinique, contrôlée, citée, auditable
```

## Démarrage rapide

```bash
# 1. Environnement (Python 3.12+) — dépendances verrouillées (uv.lock)
make setup            # ou : pip install -e ".[dev]" / uv sync

# 2. Diagnostic système 16 contrôles (sans GPU, sans réseau)
make diagnostics

# 3. Construire les index RAG depuis le corpus embarqué
make index

# 4. Cas de démonstration : fièvre + retour de Côte d'Ivoire
make demo

# 5. Lancer l'API + dashboard (http://localhost:8000)
make api

# 6. Tests complets (déterministe, aucun modèle requis)
make test

# 7. Évaluation scientifique complète (17 suites, exit code CI)
python scripts/run_evaluation.py

# 8. Migrations de schéma
python scripts/migrate.py history && python scripts/migrate.py upgrade
```

## Couverture de construction — 100 % sur les 8 domaines

| Domaine | Couverture | Preuve d'exécution |
|---|---|---|
| Domain + Core + Clinical Engine | **100 %** | 358 tests, 170 règles lint OK, 7 fixtures YAML |
| AI Mesh (registry/routing/gateways/clients/agents) | **100 %** | contrats 10/10, invariants 0 violation, matrice critique×urgence |
| Safety + Guards + Response | **100 %** | invariants G1-G7, refus 6/6, hallu 4/5, dangereux 9/9 |
| RAG (retrieval/reranking/validation) | **100 %** | recall@10 ≥ 0.90, nDCG ≥ 0.75, manifests SHA-256 |
| Ingestion/Normalisation/Chunking | **100 %** | PDF/HTML/TXT/MD → quarantaine, 30 tests |
| Évaluation scientifique | **100 %** | 17 suites / 17 PASS, rapports JSON+MD |
| Persistance ORM multi-tables | **100 %** | 12 tables normalisées + double écriture |
| Migrations | **100 %** | 4 migrations chaînées aller-retour + CLI |

Chaque ligne est revérifiable par `make diagnostics` (16 contrôles) et
`python scripts/run_evaluation.py` (exit code non nul en CI en cas de
régression sous seuil).

## Nouveautés V1.4 — complétude industrielle

- **Pipeline d'ingestion documentaire** : PDF (pypdf ou extracteur interne
  zlib pur), HTML (stdlib, script/style neutralisés), TXT/MD → nettoyage →
  sections cliniques → terminologie canonique → chunks annotés (force de
  recommandation, maladies, symptômes, tests) → **quarantaine** jusqu'à
  validation humaine (`scripts/ingest_document.py --promote`).
- **Manifests de corpus** : source/version/**intégrité SHA-256** — toute
  falsification d'une unité de preuve est détectée
  (`scripts/build_integrity_manifest.py --verify --strict`).
- **Index RAG persistants** : BM25 + vecteurs sérialisés avec invalidation
  par empreinte de corpus (reconstruction automatique si évolution).
- **ORM multi-tables + migrations** : 12 tables normalisées (patients,
  clinical_cases, travel, symptoms, diagnoses, diagnostic_tests, medications,
  evidence_usage, sources, models_registry, inferences, audit_events_orm),
  double écriture legacy-audit + relationnel, migrations versionnées
  idempotentes (0001→0004) avec `scripts/migrate.py`.
- **Évaluation scientifique** : 17 suites exécutables offline — recall/
  precision/MRR/MAP/nDCG, exactitude des citations, invariants G1-G7,
  hallucination, sorties dangereuses, latence p95, VRAM vs topologie,
  taux de recouvrement des pannes. Rapports dans `evaluation/reports/`.
- **Guards éclatés** : chaque garde dans son module (input/autonomous/
  evidence/hallucination/clinical/output) + moteurs safety dédiés
  (médicamenteuse avec catégories grossesse D/X, LLM, preuve).
- **Capacités déclaratives du mesh** : `configs/ai/model_capabilities.yaml`
  fusionné dans le registre — autonomous_diagnosis=false INVARIANT non
  surchargeable, capacités par modèle résolues dynamiquement (zéro dérive).
- **Dépendances verrouillées** : `uv.lock` (32 paquets, reproductibilité totale).

## Ce qui fonctionne immédiatement (mode déterministe)

- **Rule Engine** : suspicion paludisme/dengue/typhoïde/arboviroses, red flags,
  escalade, contraintes thérapeutiques — à partir de règles YAML auditables.
- **Populations vulnérables (V1.1)** : drépanocytose (fièvre = urgence, syndrome
  thoracique aigu, AVC, séquestration splénique) et grossesse (paludisme
  gestationnel, terme/trimestre, contre-indications : primaquine, SP 1er
  trimestre, AINS 3e trimestre, doxycycline).
- **Soins critiques & résistances (V1.2)** : typhoïde XDR (drapeau voyage Asie du
  Sud + antibiogramme, azithromycine/méropénème, contre-indications FQ/C3G),
  dengue pédiatrique (choc compensé/décompensé, remplissage prudent 10-20 mL/kg,
  critères d'intubation + ventilation protectrice, phase critique), paludisme
  rénal (AKI critère OMS, conversion µmol/L→mg/dL automatique, indications
  d'épuration extrarénale selon le niveau de structure).
- **Export DHIS2 (V1.2)** : indicateurs de surveillance agrégés hebdomadaires
  au format dataValueSets JSON / CSV / ADX 2.0 XML, file d'attente offline pour
  districts à connectivité intermittente, aucun envoi réseau implicite —
  `POST /api/v1/export/dhis2` + `scripts/export_dhis2.py`.
- **Correspondance UID MSP-CI (V1.3)** : un seul YAML à éditer
  (`configs/integrations/dhis2.yaml` : 19 indicateurs documentés, 14 org units
  district, jeu de données, COC) + validateur `scripts/validate_dhis2_uids.py`
  (format UID DHIS2, placeholders, verdict prêt-pour-push, `--strict`/`--json`)
  + procédure officielle `docs/integrations/dhis2-correspondance-msp-ci.md`.
- **Branchement Ollama testé E2E (V1.3)** : serveur mock
  `scripts/mock_ollama_server.py` (répétition générale sans GPU) et
  `scripts/med42_xdr_synthesis_test.py --mock` (32 contrôles : synthèse
  Med42 citée et auditée sur cas modéré, suspension automatique sur cas
  sévère, dégradation gracieuse) ; le même script se branche sur vos vrais
  nœuds via `TROPIRAG_OLLAMA_NODES`.
- **Leptospirose (V1.3)** : triade fièvre-myalgies-conjonctives + eaux
  stagnantes/rizières, maladie de Weil (ictère + AKI → pénicilline G IV,
  AINS interdits), hémorragie alvéolaire, myocardite, notification sanitaire.
- **Méningocoque pédiatrique (V1.3)** : signes du nourrisson (fontanelle
  bombée, irritabilité inconsolable, refus alimentaire), purpura fulminans
  (ceftriaxone IM AVANT transfert, sans attendre la PL), sepsis grave,
  prophylaxie des contacts (protocole national).
- **Carte des éclosions (V1.3)** : `/map.html` — 14 districts sanitaires CI
  (cohérents DHIS2), comptage déterministe par analyses persistées, signal
  d'éclosion (+2 cas vs semaine précédente), saisie région dans la PWA terrain
  → boucle fermée saisie → règles → carte ; API `GET /api/v1/surveillance/map`.
- **Moteur temporel** : fenêtres d'incubation, compatibilité chronologie voyage/symptômes.
- **Evidence Engine** : BM25 + vectoriel (hashing déterministe) + fusion RRF +
  reranking lexical, validation de sources, citations obligatoires.
- **Safety Gate** : refus, escalade, garde-fous anti-hallucination et
  anti-diagnostic-autonome.
- **API + Dashboard + Mobile** : FastAPI, audit trail, interface web intégrée,
  PWA terrain offline-first sur `/mobile`.

## Le mesh IA (branchable)

Chaque modèle a un rôle précis derrière un routeur par capacité :

| Capacité | Modèle | Rôle |
|---|---|---|
| speech_to_text (dictée) | MedASR | dictée clinique |
| speech_to_text (conversation) | Whisper Large v3 | multilingue / terrain |
| image_understanding | MedGemma-4B-IT | analyse image contextualisée |
| image_triage | MiniCPM-V 2.6 | screening / second avis |
| clinical_reasoning | Med42 v2 70B | synthèse clinique encadrée |
| biomedical_synthesis | OpenBioLLM 70B | synthèse littérature / dossiers |
| logical_audit | DeepSeek-R1-Distill | cohérence, contradictions |
| embeddings | BGE-M3 | retrieval hybride |
| reranking | Qwen Reranker | reranking cross-encoder |

Activation : `TROPIRAG_INFERENCE_MODE=ollama` (ou `vllm`) + `make pull-models`.
Voir `docs/operations/MODEL_INSTALLATION.md`.

**Branchement réel multi-nœuds (V1.1)** — 4 nœuds × 8 GPU × 48 Go :

```bash
export TROPIRAG_OLLAMA_NODES="speech=http://node1:11434,vision=http://node1:11434,embeddings=http://node1:11434,reranking=http://node1:11434,text=http://node2:11434"
curl http://localhost:8000/api/v1/inference/nodes   # santé réelle du mesh
```
Guide complet : `deployment/ollama/README.md` (setup_node.sh, health_check.sh,
Modelfiles cliniques, répliques croisées node2↔node3, repli déterministe).

## Structure (extrait)

```
src/tropirag/
├── core/              # config, enums, résultats, erreurs
├── domain/            # patient, cas, voyage, symptômes, maladies, médicaments
├── clinical_engine/   # règles, sécurité, temporal, différentiel  ← AUTORITÉ
├── evidence_engine/   # ingestion, chunking, retrieval, reranking, validation
├── query_engine/      # intentions, filtres juridiction/temporel, exigences
├── ai/                # registry, router, gateways, agents, guards  ← MESH
├── safety/            # safety gate, médicamenteuse, audit, privacy
├── response_engine/   # réponse clinique citée, multilingue
├── persistence/       # SQLite 12 tables ORM + migrations + UoW
├── observability/     # logs, métriques, traçage
└── api/               # FastAPI + middleware + dashboard
```

```
evaluation/            # 17 suites scientifiques + datasets + rapports
migrations/            # 4 migrations versionnées + engine stdlib pure
rules/fever_travel/tests/  # fixtures comportementales YAML par famille
```

## Sécurité & limites d'usage

TropiRAG **ne pose jamais de diagnostic autonome**. Toute sortie est une aide à
la décision destinée à un professionnel de santé, adossée à des sources citées
et à des règles explicites. Voir `docs/governance/SAFETY_INVARIANTS.md`.

## Licence

Propriétaire — © 2026 SIGH-CI. Tous droits réservés.

## Contact

- **DSI** : dsi@sigh.ci
- **DPO** : dpo@sigh.ci
- **Helpdesk** : helpdesk@sigh.ci
- **Site** : https://sigh.ci
