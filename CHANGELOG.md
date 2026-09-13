# Journal des changements — MEDISUITE

Format Keep a Changelog ; versionnement sémantique ; les numéros de release
correspondent aux tags Git.

## [v0.9.0] — 2026-09-14

### Écran promoteur « Study Status / Lock » (portal, v0.9)
- `apps/web-portal/src/features/study/StudyStatus.tsx` (route `/study`) :
  cockpit de pilotage de MEDISUITE-CI-01 fondé sur les endpoints eCRF v0.8
  **sans modification backend** — timeline R5→R8 du plan de validation
  (phase active dérivée de l'état réel : base ouverte → R6, verrou posé →
  R7), cartes verrou/checksum/témoins/sujets/entrées/requêtes SDV, agrégats
  DSMB sans PHI (sujets par site/scénario, EI/SAE + règle d'arrêt, médiane
  P3), références du dossier d'investigation.
- **Action de verrouillage M+18 pilotable à l'écran** (rôle promoteur) :
  ≥ 2 témoins distincts + confirmation typée « VERROU MEDISUITE-CI-01 » ;
  les préconditions sont affichées AVANT l'action (`lockReadiness`,
  réplique exacte des gardes serveur) et la garde serveur reste
  fail-closed (422/409/403). Lecture réseau vivante : rien n'est mis en
  cache offline (les indicateurs de pilotage ne survivent pas à une
  coupure) — 14 tests vitest (`status-logic.ts` pur) ; 19/19 au total.

### ADR-0026 — rapport d'évaluation clinique MEDDEV 2.7/1 rev 4 (R7)
- `docs/adr/0026-rapport-clinique-meddev-271.md` : le CER sera rédigé selon
  MEDDEV 2.7/1 rev 4, alimenté uniquement par des sources versionnées —
  pipeline figé **eCRF → verrou M+18 → extraction SAF → analyse SAP →
  adjudication → CER → bénéfice-risque final** ; état de l'art par requêtes
  reproductibles (PubMed/AJO, log en annexe) ; équivalence **non
  revendiquée** ; alternatives écartées argumentées (CER littérature seule
  irrecevable pour un IIb S1-S5 ; pas d'analyse hors verrou).
- **Squelette normatif TD-11**
  (`compliance/mdr/technical-documentation/11-rapport-evaluation-clinique-meddev-271.md`)
  : les 9 sections MEDDEV mappées à leur source réelle du dépôt, état
  🟢 structure / 🔴 contenu (R7, post-verrou) — auditable dès maintenant en
  revue interne (PROC-08) AVANT le démarrage de R6. Index TD mis à jour.

### Kit de signatures terrain R5 (`compliance/mdr/clinical/signatures/`)
- **Page de signatures du protocole v1.0** (7 signataires : promoteur,
  coordonnateur, RC, statisticien indépendant, data manager, DSMB, moniteur
  — déclarations de conflits jointes, amendements versionnés A1…, blocage
  d'inclusion sans chaîne complète).
- **Registre des investigateurs par site** (COC/TRI/YOP/BOU) : chaque site
  signe la version exacte exécutée, re-signature obligatoire à chaque
  amendement, vérifications du moniteur consignées au rapport A4.
- **Journal de délégation CSV** (ISO 14155 F.4.3) : tâches T3/T5/T6/T8 par
  site, signatures délégué + PI.
- Raccords : protocole §11 pointe vers le kit ; index des soumissions lie
  le kit à la ligne « accords de site » ; plan 08 (R5 outillage 🟢, R7
  structure 🟢) ; GAP-ANALYSIS note v0.9 ; `docs/E-CRF.md` documente
  l'écran promoteur.

### Qualité — idempotence locale des suites (défaut latent v0.8 corrigé)
- Le verrou M+18 étant **irréversible par conception**, la base de dev
  `data/ecrf-service.db` persistait entre les runs : toute ré-exécution
  locale de la suite eCRF échouait en 409 (la CI passait car le runner
  démarre vierge). Correctif « **BDD fraîche par run** » (principe v0.1)
  appliqué avant import dans les suites **ecrf / auth / patient / audit**
  (résidus équivalents : MFA enrôlé, utilisateurs créés, chaîne d'audit
  persistée) — idempotence prouvée par double run ; 39/39 suites services,
  127/127 packages+datasets, 47/47 IA.

## [v0.8.0] — 2026-09-14

### Couverture de l'arborescence initiale (audit mesuré)
- `docs/COUVERTURE-ARBRE-INITIAL.md` : relecture intégrale de l'arborescence
  initiale (2 674 chemins) vs dépôt réel (509 fichiers) — 108 correspondances
  exactes, 43 par famille, 401 fichiers réels **au-delà** de la spec ;
  cartographie des consolidations volontaires (ADR-0020, noyau partagé,
  écrans config-driven) et des manques assumés ; outil reproductible
  `tools/compare_arborescence.py`.

### Instruments terrain R6 (monitoring, annexe A4)
- `compliance/mdr/clinical/monitoring/` : plan de monitoring (ISO 14155
  §5.6 — visites V0/V1-V6/VC, SDV 20 %/100 % SAE, critères
  d'intensification), **modèle de rapport de visite format A4** (3 pages,
  sections système/consentements/SDV/sûreté/déviations/actions/signatures),
  **registre des déviations** central (typologie, classement majeure/mineure,
  condition de lock).

### Pilotage des soumissions (jalon R5, M+3)
- `compliance/mdr/submissions/` : tableau de bord des soumissions + checklist
  **ANOC-CI** (30 items reliés aux artefacts du dépôt), checklist **PACTR**
  (jeu de données ICTRP 24 items, valeurs protocole), checklist
  **Ministère + DPIA loi 2013-450** (chaîne critique des dépendances).

### Verrou de base M+18 et extraction data manager (§7.4 / SAP A5)
- `services/ecrf-service` : `POST /api/v1/ecrf/study/lock` — promoteur
  (`ecrf.lock`), ≥ 2 témoins, zéro requête SDV ouverte, **checksum SHA-256
  de l'état complet** (contenu canonique recalculé, pas le hash stocké),
  **irréversible** ; après lock : toute écriture → 409 (inclusion, saisie,
  amendement, sync rejetés proprement).
- `GET /api/v1/ecrf/extract` — **data manager uniquement** (`ecrf.extract`),
  **409 avant le lock** ; après : SAF pseudonymisé (dernière entrée signée
  par sujet/formulaire + dérivations SAP recalculées) ; **alarme
  d'intégrité 500** + événement `ecrf.extract.integrity` audité si l'état
  diverge du checksum verrouillé.
- `GET /api/v1/ecrf/study/status` (verrou, témoins, compteurs, checksum
  indicatif) ; RBAC v0.8 : `ecrf.lock` (promoteur), `ecrf.extract`
  (data manager) — celui qui verrouille n'extrait pas.
- Tests : 5 nouveaux cas séquentiels (23/23 ecrf-service) dont altération
  post-lock → alarme prouvée.

### ADR-0025 — Échantillonnage OTel
- `medisuite_core/observability.py` : head sampling **déterministe
  parent-based** (décision parent W3C honorée, sinon ratio déterministe sur
  le trace_id — traces toujours complètes), **always-on errors**, routes de
  bruit `/health` `/ready` `/metrics` sans span, décision propagée
  (flags `01`/`00`) et mesurable (`snapshot()`), env
  `MEDISUITE_OTEL_SAMPLING_RATIO` (défaut 1.0 pendant R6, fail-open
  assumé) — middleware `http.py` mis à jour, 6 tests (21/21 integration).
- `docs/adr/0025-otel-sampling.md` (alternatives écartées : tail sampling,
  SDK officiel, ratio aléatoire).

### CI renforcée (écart découvert par l'audit de couverture)
- Job `packages+integration` ajouté (noyau + datasets + tests
  d'intégration HAPI/OTel/IOP) ; contrôle TypeScript strict sans
  `|| true` silencieux.

## [v0.7.0] — 2026-09-14

### R6 — eCRF FHIR opérationnel (saisie → signature → monitoring → DSMB)
- **Noyau** `medisuite_core/ecrf.py` : domaine pur de l'investigation
  MEDISUITE-CI-01 — codes sujets pseudonymes (CI01-<SITE>-NNNNN),
  formulaires F01-F06 (annexe A1) avec contrôles de cohérence §8,
  dérivations SAP (éligibilité §4.2/§4.3, délai P3, détection SAE),
  idempotence (clé SHA-256 payload canonique), mapping FHIR R4 vers les
  profils IOP (Patient-CI-IOP + Observation-CI-IOP par champ) — 20 tests.
- **RBAC v0.7** : permissions `ecrf.read/write/sign/monitor/export/adjudicate`
  + rôles GCP `investigateur`, `moniteur`, `adjudicateur`, `data_manager`,
  `promoteur` ; `medecin` saisit et signe. Séparation fail-closed : le
  comité d'adjudication (aveugle) ne saisit QUE le F05.
- **Service** `services/ecrf-service` (:8205, 39ᵉ suite) : sujets, saisie
  validée 422-détaillée, signature verrouillante ISO 14155 §4.8,
  amendements versionnés (original intact), requêtes SDV
  (moniteur ouvre / site clôture), sync offline par lots ≤ 200 avec
  résultat par item, export DSMB agrégé sans PHI (EI/SAE, médiane P3,
  adhésion), audit chaîné SHA-256 persisté (rechargé au démarrage),
  poussée FHIR optionnelle vers HAPI (statuts gracieux) — 18 tests.
- **web-portal** : écran `/ecrf` opérationnel (catalogue piloté par les
  définitions du noyau, saisie offline-first, signatures) + api `submitWithQueue`.

### Mode offline du web-portal
- Service worker `public/sw.js` (PROD) : navigations et GET /api/* en
  réseau-d'abord avec repli cache ; non-GET jamais interceptés.
- File IndexedDB (`src/offline/`) : empilement FIFO, rejeu idempotent
  (`Idempotency-Key` + dédoublonnage serveur par clé calculée → zéro
  doublon), dead-letter pour rejets 4xx, back-off 1 s→30 s, bannière
  d'état `OfflineBanner`, boucle de sync (online + 30 s) — 5 tests vitest.
- Vite dev proxy `/api/ecrf` avec rewrite (comportement identique au
  proxy api-gateway).

### UDI-EID GS1 (volet codifiable)
- `medisuite_core/gs1_udi.py` : GTIN-13/14 (clé mod-10), Basic UDI-DI
  (indicateur 0), dates YYMMDD (jour 00 = fin de mois), AIs
  01/10/11/17/21 avec jeu fail-closed, élément-string DataMatrix (FNC1),
  GS1 Digital Link → EID, `label_payload`/`verify_label_payload` — 17 tests.
- `labeling.json` v0.7.0 : bloc `gs1` (émetteur GS1 CI proposé, statut
  adhésion 🔴 R8) ; `docs/UDI-GS1.md` (chemin d'attribution réel).
- Écran « À propos » : données GS1 servies par `GET /api/v1/about`.

### Infrastructure & docs
- `services/registry.py` : ecrf-service (:8205) ; REGISTRY api-gateway
  enrichie ; proxy Vite.
- Docs : `docs/E-CRF.md`, `docs/OFFLINE-PORTAL.md`, `docs/UDI-GS1.md` ;
  compliance : plan R6 outillage ✅, protocole §8 note eCRF 🟢, GAP note.
- Validation : 80 tests packages+ecrf-service, 39/39 suites services,
  portal tsc strict + build + vitest verts.

## [v0.6.0] — 2026-09-14

### R5 — Protocole d'investigation clinique multicentrique détaillé
- `compliance/mdr/technical-documentation/10-protocole-investigation-multicentrique-R5.md` :
  **MEDISUITE-CI-01** (ISO 14155:2020, MDR Annexe XV, art. 62-80) — design
  prospectif multicentrique intra-patient apparié (CHU Cocody, Treichville,
  Yopougon ; extension Bouaké), 5 scénarios critiques S1-S5, co-endpoints
  primaires (κ pondéré ≥ 0,80 IC95 borné ; sûreté 30 j ; délai priorisation),
  référence adjudiquée par comité indépendant, calcul d'effectif justifié
  (n=600, 200/site — supersede l'estimation 300-500/site avec note d'écart),
  gestion des événements indésirables + règles d'arrêt DSMB, eCRF sur profils
  FHIR IOP (ADR-0024), pseudonymisation/DPIA (loi 2013-450), ANOC-CI + PACTR,
  calendrier R5 M+2→M+6 et annexes A1-A6. Soumissions/signatures : 🔴.
- `06-evaluation-clinique.md` + `00-index…` + `08-plan…` mis à jour en
  conséquence.

### R2 — Écran « À propos » UDI (écart 🔴 clôturé)
- **Noyau** : `create_service_app` expose désormais `version` + `commit`
  (`MEDISUITE_VERSION`/`MEDISUITE_COMMIT`) sur `/health` des 38 services
  (étiquetage §2 règle 1) + 3 tests (`test_http_factory.py`).
- **api-gateway** : `labeling.json` versionné + `GET /api/v1/about` PUBLIC
  (MDR Annexe I §23.2) avec surcharge env au déploiement + 2 tests.
- **web-portal** : écran `About.tsx` (identification produit/réglementaire,
  Basic UDI-DI, UDI-EID état, classe IIb, marquage CE ❌ affiché, IFU,
  symboles, avertissement) + route `/about` + nav + i18n fr/en ; repli
  hors-ligne honnête (`VITE_APP_VERSION`).

### Datasets synthétiques des 26 modules (écart 🟠 clôturé)
- `datasets/` : `registry.py` (features cliniques nommées + schémas de labels
  par tâche), `generate.py` (déterministe, flux RNG par module seed*100+no,
  signal apprenant, modalités manquantes ADR-0018 : ≤1, jamais la primaire),
  `manifest.json` (SHA-256 par fichier, note légale), 26 jeux train(120)/
  val(30) JSONL alignés sur les configs IA, README, **6 tests** (manifest,
  intégrité SHA-256, schéma par tâche, déterminisme bit-à-bit, signal,
  politique ADR-0018).

### Audit des 26 modules
- `docs/audit-26-modules.md` + `tools/audit_26_modules.py` (+ données
  `docs/_audit_data.json`) : matrice Module/Service/AI/Datasets/Configs
  vérifiée par les artefacts, écarts corrigés en v0.6.0 et limites restantes
  (entraînement réel → R6, campagne GPU CHU → R4, i18n/offline → backlog).

## [v0.5.0] — 2026-09-14

### Jalons réglementaires R1-R4 (dossier CE v1.0.0)
- **R1 — SMQ ISO 13485** : `compliance/smq/` — index (engagement direction,
  cartographie) + 8 procédures (maîtrise documentaire, gestion des risques,
  revue de conception/V&V, incidents/CAPA, fournisseurs, formation,
  libération, audit interne/revue de direction), chacune avec finalité,
  flux, enregistrements et indicateurs.
- **R2 — IFU** : `compliance/mdr/technical-documentation/ifu/` — 4 notices
  (clinicien, technicien, administrateur, patient) avec avertissements
  critiques, tableaux de tâches/écrans, limites + étiquetage UDI (Basic
  UDI-DI, règles de version, écarts déclarés).
- **R3 — Usabilité formative** : protocole IEC 62366 prêt à passer
  (5 scénarios critiques avec critères chiffrés, NASA-TLX, automation bias)
  + grille de passation par participant.
- **R4 — Durcissement** : `security/hardening/` — Vault (service compose
  DEV + policy HCL moindre privilège + script d'initialisation), mTLS
  (générateur PKI de test vérifié, config NGINX mTLS HAPI, checklist
  ASVS), plan de tests d'intrusion (ASVS V2-V5, OWASP API Top 10, scénarios
  métier rtPA/extraction) ; **générateur SBOM CycloneDX stdlib**
  (8 composants, 141 références composant→service) + snapshot réglementaire.

### ADR-0024 — profils FHIR nationaux IOP-CI candidats
- `services/integration-service/fhir/profiles/` : StructureDefinition
  Patient-CI-IOP (identifiant national OID obligatoire, CNAM secondaire,
  extension région sanitaire), Observation-CI-IOP (LOINC/UCUM), CodeSystem/
  ValueSet identifiants, exemple patient, implementation-guide.
- `medisuite_core/iop.py` : validateurs purs (identifiant national
  `^[A-Z0-9]{10,16}$`, CNAM 10 chiffres, région — liste partielle assumée
  fail-closed), mapping `patient_to_iop`, catalogue des profils.
- Hub : `GET /api/v1/fhir/profiles` + `POST /api/v1/fhir/server/patients/iop`
  (RBAC `patient.write`, 422 sur non-conformité, événement bus) — validation
  côté hub + validation HAPI : défense en profondeur.

### Banc de performance d'inférence (critère EGSP p95 ≤ 2 s)
- `tools/bench/bench_fusion.py` : charge synthétique reproductible (seed
  42), backends numpy/torch, scénario dégradé `--missing-ratio`, p50/p95/
  p99 + débit, verdict PASS/FAIL (exit 1), JSON horodaté versionné.
- Référentiels réels CPU (module 8) : numpy **p95 0,32 ms** (3 535 req/s),
  torch 2.14+cpu **p95 0,79 ms** (1 481 req/s), 30 % modalités manquantes
  **0,65 ms** — PASS ; méthodologie + protocole GPU CHU dans
  `docs/BENCHMARK-GPU.md`.

### Tests
- integration-service **15/15** (3 tests IOP : validateurs + 6 cas
  invalides, catalogue 4 profils, création IOP avec profil/meta/région +
  RBAC 403 + 422 non-conformité) ; packages 81/81 ; 38/38 suites services.

## [v0.4.0] — 2026-09-14

### Serveur FHIR R4 réel — HAPI JPA
- **Référentiel central d'interopérabilité** : `hapiproject/hapi` sur
  PostgreSQL 16 dans `docker-compose.minimal.yml` (9 → 11 services),
  configuration `local-deployment/hapi/application.yaml` (FHIR R4 4.0.1,
  validation serveur REQUIRE, JSON par défaut, rest-hook activé).
- `medisuite_core/hapi_client.py` : client REST FHIR R4 stdlib
  (metadata/ping/create/read/search/transaction), injection d'opener pour
  les tests, **dégradation gracieuse** (serveur hors ligne → reachable=false,
  jamais d'exception vers le clinicien).
- integration-service : 5 endpoints `/api/v1/fhir/server/*` (status,
  metadata, recherche patients, création Patient) avec **RBAC fail-closed**
  (`patient.read`/`patient.write`) + événement bus `fhir.patient.created` ;
  documentation `docs/FHIR-HAPI.md`.

### Télémétrie OpenTelemetry native (stdlib)
- `medisuite_core/observability.py` : propagation **W3C Trace Context**
  (traceparent parse/émission, headers invalides ignorés), spans serveur,
  **export OTLP/HTTP JSON** vers un collecteur par lots (thread daemon,
  tampon 2 048 spans, back-off silencieux) — télémétrie sans dépendance ni
  risque pour le service.
- **Point d'instrumentation unique** : middleware dans
  `medisuite_core.http.create_service_app` — les 38 services produisent
  désormais des spans (méthode, route, statut, durée, request_id) sans
  modification de code.
- `monitoring/otel/collector.yaml` : otel-collector-contrib 0.109.0
  (OTLP/gRPC 4317 + OTLP/HTTP 4318 → métriques Prometheus 8889 + debug) ;
  job Prometheus `otel` ; documentation `docs/OTEL.md`.

### Déploiement Kubernetes GPU
- Overlay `infrastructure/kubernetes/gpu/` : RuntimeClass nvidia, device
  plugin v0.16.2 avec **time-slicing ×2** (coût GPU ÷2 pour l'inférence),
  PriorityClass, Deployment `multimodal-gateway` (`nvidia.com/gpu: 1`,
  runAsNonRoot, probes), Service + **HPA cpu 70 % 2→6**, kustomization ;
  compromis d'ingénierie documentés dans `docs/K8S-GPU.md`.

### Démarrage du dossier de marquage CE (jalon v1.0.0)
- `compliance/mdr/technical-documentation/` : **dossier technique MDR
  2017/745 Annexe II/III structuré et partiellement rédigé** — index avec
  états (🟢/🟠/🔴), identification + classification règle 11 (IIb
  justifié), EGSP Annexe I (exigence↔preuve↔test), FMEA ISO 14971 (10
  risques cliniques RM-01…RM-10 avec mesures et RPN), IEC 62304 classe C
  (mapping processus↔preuves 373+ tests), plan IEC 62366 (5 scénarios
  critiques d'usage), stratégie d'évaluation clinique multicentrique CHU
  (design, endpoints, tailles), plan PMS/vigilance/PMCF, cartographie SMQ
  ISO 13485, **plan de mise en conformité v1.0.0** (jalons R1-R9 datés).

### Tests et validation
- integration-service 12/12 (5 tests HAPI : hors ligne, metadata, search,
  création + RBAC auditeur 403, payload FHIR envoyé ; 3 tests OTel :
  traceparent roundtrip + 5 invalides, span middleware + propagation,
  payload OTLP conforme).
- packages 81/81 verts (core, clinical-rules, fusion IA).

## [v0.3.0] — 2026-09-13

### Visualiseur OHIF v3 branché sur /dicom-web
- **Chaîne d'imagerie réelle de bout en bout** : STOW → Orthanc → DICOMweb
  (PS3.18) → OHIF → lecture diagnostique. Conteneur `ohif-viewer`
  (`ohif/app:v3.8.3` surchargé) dans `docker-compose.minimal.yml`, UI port 3001.
- `local-deployment/ohif/app-config.js` : source de données DICOMweb
  `orthanc` (QIDO-RS/WADO-RS en chemins relatifs, lazy-load des études,
  transfert JPEG Lossless).
- `local-deployment/ohif/nginx.conf` : proxy `/dicom-web` + `/wado` →
  `orthanc-pacs:8042` avec **authentification injectée côté serveur** — le
  secret PACS ne quitte jamais le conteneur, aucun CORS, aucune exposition
  navigateur.
- imaging-service : `GET /api/v1/pacs/viewer-url?study_uid=…` — lien profond
  OHIF (`/viewer?StudyInstanceUIDs=…`) avec RBAC `imaging.read` et **validation
  stricte d'UID DICOM** (`^\d+(\.\d+)+$`, anti-injection) ; 4 tests nouveaux.
- web-portal (page Imagerie) : bouton **OHIF ↗** par étude (base surchargeable
  `VITE_OHIF_BASE`).
- Documentation : `docs/OHIF-VIEWER.md` (architecture, démarrage, sécurité,
  limites connues — plugin Keycloak recommandé en production).

### IA — fusion torch ENTRAÎNABLE de bout en bout (ADR 0023)
- `ai/multimodal/core/torch_fusion.py` : `TorchFusionModel` (nn.Module,
  float64) — projections `nn.Linear` par modalité, **cross-attention
  multi-têtes** (`TorchCrossAttention` : Wq/Wk/Wv/Wo, softmax √(d/h)),
  **portes sigmoid nn.Parameter** par modalité, **requête globale apprise**,
  **tête de tâche entraînable** (`TorchTaskHead` : binaire / multiclasse /
  régression).
- **Équivalence NumPy à l'initialisation** (pattern ADR 0022 étendu au tronc) :
  tous les poids copiés du socle déterministe v0.1 — Δ probabilité = 0 au
  premier predict, tenseur `fused` allclose rtol 1e-6 ; divergence uniquement
  par entraînement explicite.
- `fit()` déterministe : Adam, ordre fixe (aucun shuffle), tokenisation gelée
  pré-calculée, pertes BCE-with-logits / CE / MSE, historique retourné —
  démontré sur synthétique séparable : perte 2,01 → 0,16, **accuracy 100 %**,
  deux fits identiques → historiques identiques (zéro RNG).
- Checkpoints natifs `state_dict` + métadonnées (`medisuite-fusion-0.3`) :
  round-trip bit-à-bit testé, prêt pour MLflow.
- `predict()` aux clés identiques à `FusionEngine.infer` (drop-in) :
  importance des modalités APPRISE, recalibrage ADR-0018 conservé, gradient
  épars sur modalités absentes (comportement testé).
- Factory : `fusion_model_from_config()` / `fusion_model_for_module()` ;
  périmètre honnête : survival/segmentation rejetées `NotImplementedError`.
- Suite IA : **16 tests** nouveaux (`test_torch_fusion.py`), tous verts
  (torch 2.14+cpu).

### Divers
- Badge README → v0.3.0 ; 22 ADR → 23 (ADR 0023) ; roadmap mise à jour :
  FHIR R4 (HAPI), télémétrie OTel et K8s GPU reportés en v0.4.0.
- `docker-compose.minimal.yml` : 9 services (+ ohif-viewer).

## [v0.2.0] — 2026-09-13

### Écrans cliniques spécialisés (web-portal)
- **Lecteur BI-RADS** (`/birads`) : lecture mammographique structurée — densité
  ACR a-d, masse, microcalcifications, asymétrie, aire axillaire — catégorisation
  BI-RADS 1-6 avec échelle colorée et conduite à tenir (ACR BI-RADS 5e éd. 2013),
  calcul via oncology-service (moteur `packages/clinical-rules`).
- **Code AVC** (`/code-avc`) : horloge « dernier vu normal » avec bandeau des
  fenêtres thérapeutiques AHA/ASA (alteplase ≤ 4,5 h, thrombectomie ≤ 6 h,
  perfusion 6-24 h DAWN/DEFUSE-3), cotation NIHSS 11 items (0-38), ASPECTS
  10 régions cliquables, checklist des contre-indications à la thrombolyse et
  synthèse d'orientation double validation (neurologue + neuroradiologue).
- `api.postScore` désormais générique (typage strict des réponses) ;
  design system étendu (échelle BI-RADS, bandeau fenêtres, grille ASPECTS,
  bannière go/caution/stop). `tsc -b` strict + build Vite OK.

### IA — backends de calcul (ADR 0022)
- `BaseEncoder.project()` : point d'injection unique des projections
  entraînables ; le socle NumPy déterministe reste le défaut (v0.1 figée).
- Backend **PyTorch** : `TorchProjector` (nn.Linear float64) dont les poids
  sont copiés depuis la matrice stable P → sortie numériquement identique au
  socle NumPy à l'initialisation (tokens allclose rtol 1e-6 ; dict d'inférence
  complet inchangé après branchement — tests à l'appui).
- Backend **MONAI** : prétraitement image canonique (EnsureChannelFirst →
  ScaleIntensity → Resize 64×64 / 32³) inséré dans la tokenisation
  `imaging_2d` / `imaging_3d`.
- Clé YAML `backend: numpy|torch|monai` dans les 26 configurations de modules ;
  import paresseux + `ImportError` documentée ; suite IA : **31/31** avec
  torch 2.14+cpu et MONAI installés.

### PACS — Orthanc réel (ADR 0006 appliqué)
- `services/imaging-service/src/orthanc_client.py` : client REST stdlib
  (urllib/base64) — `system`, `ping`, `studies` (expansion), relais QIDO-RS ;
  configuration par variables `MEDISUITE_ORTHANC_*` ; dégradation gracieuse.
- Endpoints `/api/v1/pacs/status` (jamais 5xx), `/api/v1/pacs/studies`,
  `/api/v1/pacs/qido` ; `integrations` reflète l'état réel. 12/12 tests imaging.
- `docker-compose.minimal.yml` **réparé** (YAML invalide en v0.1 : argument de
  build non quoté, nom de volume incohérent) et Orthanc réel
  `orthancteam/orthanc:24.9` avec configuration complète
  (`local-deployment/orthanc/orthanc.json` : DICOMweb activé, AE `MEDISUITE`,
  modalités de simulation, authentification, volume persistant).
- Documentation : `docs/PACS-ORTHANC.md`.

### Divers
- Badge de version README → v0.2.0 ; 21 ADR → 22 (ajout ADR 0022).

## [v0.1.0] — 2026-09-13

### Fondations
- Monorepo complet : 38 services, 26 modules de spécialités (ports 8100-8123),
  4 passerelles, 5 transverses ; api-gateway avec proxy JWT + token bucket.
- `packages/medisuite-core` : JWT HS256, scrypt, TOTP RFC 6238, RBAC
  fail-closed, audit chaîné SHA-256, HL7 v2.5 (parser + MLLP), FHIR R4,
  bus d'événements, seed ivoirien.
- `packages/clinical-rules` : ~90 scores cliniques tracés vers leurs
  référentiels (ESI/CTMP, qSOFA/SOFA, GCS, Wells, Parkland, ISS, CURB-65,
  CHA2DS2-VASc, HEART, GOLD, CKD-EPI 2021, KDIGO, kt/V, BI-RADS, Fleischner,
  Lung-RADS, AJCC 8e, IOTA, ASPECTS, NIHSS, MMSE, PHQ-9, Westgard…).
- Moteur de fusion multimodale NumPy déterministe : cross-attention softmax
  + gated fusion + MissingModalityHandler, 7 encodeurs, 6 têtes, 26 configs
  YAML ; stack MLOps (MLflow, DVC, Feast, Airflow, Kubeflow, KServe).
- web-portal Vite/React/TS strict + patient-portal RGPD + CLI TypeScript ;
  infrastructure Docker/K8s/Helm/Terraform/ArgoCD/Flux, monitoring Prometheus
  avec alertes cliniques/IA, OPA Rego, realm Keycloak, GAP-ANALYSIS honnête.
- Validation : 373 tests verts (105 packages + 268 services, 38/38 suites).
