# Analyse d'écarts réglementaire — MEDISUITE v0.4.0

> **Mise à jour v0.15.0** : images GHCR (6 services cœur, tags
semver/sha, job CI conditionné aux suites vertes), NetworkPolicy k8s
deny-par-défaut + allowlist minimale (DNS, intra-namespace, gateway) et
overlays **staging/prod** (namespaces distincts, répliques, PDB) — le bloc
« GHCR + NetworkPolicy, multi-env » est fermé. Reste codeable :
mobile/desktop (v1+, assumé).

> **Mise à jour v0.14.0** : 96 écrans fins générés (24 modules × 4 types)
depuis les sources de vérité — le bloc « ~100 écrans spécialisés fins » de
l'audit de couverture est fermé (gabarits typés + calculateurs de scores
réels + assistance IA avec avertissement de validité). Reste codeable :
GHCR/NetworkPolicy, mobile/desktop (v1+).

> **Mise à jour v0.13.0** : setup local assisté (séquence 00-10
idempotente + `make setup-local`) et paquet hors-ligne air-gapped
(`build-bundle.sh` + MANIFEST.sha256 + `install-bundle.sh`) — le bloc
« scripts setup 00-10 + packages offline `.tar` » de l'audit de couverture
est fermé. Makefile re-réparé (TAB) avec test verrou CI anti-récidive.
Reste codeable : écrans fins, GHCR/NetworkPolicy, mobile/desktop (v1+).

> **Mise à jour v0.12.0** : e2e Playwright (5 parcours, APIs mockées, job CI)
et charge k6 verrouillée (smoke/stress, seuil EGSP p95 ≤ 2 000 ms, workflow
dispatch) — le bloc « e2e Playwright/charge k6 » de l'audit de couverture
est fermé au niveau instruments ; l'exécution avec trafic CHU reste 🔴
R6-R7. Makefile réparé (tabs). Reste codeable : setup local 00-10,
écrans fins, GHCR/NetworkPolicy, mobile/desktop (v1+).

> **Mise à jour v0.11.0** : usabilité sommative IEC 62366-1 rédigée
(protocole 8 scénarios reliés aux dangers + grille + modèle de rapport,
index TD §7 → 🟠 ; exécution 🔴 R6 sur interface congelée) ; i18n du
portal implémenté RÉELLEMENT (fr/en/ar RTL/es, 43 clés × 4, parité
compile-time + 6 tests) — l'actif mort `translations.json` est désormais
consommé ; CI GPU self-hosted optionnelle (dispatch). Reste 🔴 : exécutions
terrain (R3 sommatif, R6, pentest, GPU CHU) et backlog §ci-dessous.

> **Mise à jour v0.10.0** : model-cards formelles ×26 (`compliance/mdr/model-cards/`,
> MC-01…MC-26 + index) générées par outil depuis les sources de vérité du dépôt
> (datasets/registry.py, configs IA, audit 26 modules) — 6 tests verrouillants
> (déterminisme, complétude, alignement sources, honnêteté des métriques) et
> idempotence CI (`--check`). Le bloc 🔴 « model-cards » de l'audit de
> couverture est fermé au niveau structure ; les métriques restent 🔴 R6-R8
> (verrou M+18 → SAP → CER TD-11).

> **Mise à jour v0.9.0** : écran promoteur « study status/lock » (portal,
> endpoints eCRF v0.8 — verrou M+18 pilotable à l'écran avec confirmation
> typée + 2 témoins), ADR-0026 (rapport clinique MEDDEV 2.7/1 rev 4) +
> squelette normatif TD-11 mappé aux sources du dépôt, kit de signatures
> terrain R5 (page v1.0, registre investigateurs, journal de délégation
> ISO 14155 F.4.3). Reste 🔴 : exécutions terrain (signatures réelles,
> soumissions ANOC/PACTR, inclusions R6, contenu CER R7).

> **Mise à jour v0.8.0** : couverture de l'arborescence initiale mesurée
> (`docs/COUVERTURE-ARBRE-INITIAL.md`), instruments terrain R6 rédigés
> (monitoring A4, registre déviations), checklists de soumission
> ANOC-CI/PACTR/Ministère-DPIA, **verrou de base M+18 + extraction SAF du
> data manager opérationnels** (R6 outillage complet), ADR-0025 sampling
> OTel. La validité clinique des sorties IA reste 🔴 **par conception**
> jusqu'à l'exécution de l'investigation (R6-R8).

> **Mise à jour v0.7.0** : eCRF FHIR opérationnel (`services/ecrf-service`
> + écran portal offline-first — jalon R6 volet outillage 🟢), mode
> offline du web-portal (SW + file idempotente), UDI-EID GS1 volet
> codifiable (`medisuite_core/gs1_udi.py`). La validité clinique des
> sorties IA reste 🔴 **par conception** jusqu'à l'exécution de
> l'investigation (R6-R8).

> **Mise à jour v0.6.0** : protocole d'investigation R5 rédigé
> (`10-protocole-…-R5.md`, MEDISUITE-CI-01), écran « À propos » UDI livré
> (`/api/v1/about` + web-portal), datasets synthétiques 26 modules + audit
> reproductible (`docs/audit-26-modules.md`). Les lignes ci-dessous restent
> référencées à la v0.4 ; les jalons R2/R5 concernés sont marqués dans
> `08-plan-validation-v1.0.0.md`.

> Honnêteté d'ingénieur : ce tableau distingue ce qui est **implémenté**, ce qui est
> **documenté mais à exécuter**, et ce qui **manque** avant toute utilisation clinique.
> Mise à jour v0.4 : le dossier technique de marquage CE est **structuré et
> partiellement rédigé** dans `mdr/technical-documentation/` (11 documents,
> états 🟢/🟠/🔴 par section) — la colonne v0.4 remplace la v0.1.

| Exigence | Statut v0.1 | **Statut v0.4** | Écart / action (→ jalon plan v1.0) |
|---|---|---|---|
| MDR 2017/745 — classification | ⚠️ postulat IIb (ADR-0004) | 🟠 classification règle 11 **justifiée par écrit** (`01-identification-classification.md`) | Rapport de classification final + notifié (R8) |
| Dossier technique (Annexe II/III) | 🔴 inexistant | 🟠 11 documents structurés : EGSP, FMEA, 62304, 62366, clinique, PMS, SMQ | Sections 🔴 : IFU, usabilité sommative, investigation clinique (R2, R3, R5-R7) |
| ISO 13485 (SMQ) | 🔴 non implanté | 🟠 cartographie processus + évaluation fournisseurs rédigées (`09-smq-iso13485.md`) | Procédures DOC-01/CAPA/formation + audit interne (R1) |
| IEC 62304 (logiciel, niveau C) | 🟠 architecture testée, lifecycle non audité | 🟠 mapping processus↔preuves 373+ tests (`04-iec-62304-classe-C.md`) | Revues de conception formelles, couverture archivée |
| ISO 14971 (gestion des risques) | 🟠 risques projet R1-R10 | 🟠 **FMEA clinique RM-01…RM-10** avec mesures + RPN + bénéfice-risque (`03-…`) | Clôture RM-02/05/07/09 avant pilote |
| IEC 81001-5-1 (traçabilité) | ✅ audit chaîné | ✅ audit chaîné + **télémétrie OTel 38 services** (W3C + OTLP, v0.4) | Traces inter-service sortantes (v1.0) |
| RGPD art. 7 (consentements) | ✅ consentements révocables | ✅ idem | DPIA complets (5 modules) |
| RGPD art. 32 (sécurité) | 🟠 scrypt, JWT, pseudonymisation | 🟠 idem + RBAC prouvé + validation serveur HAPI | Vault + mTLS + pentest (R4) |
| HDS (hébergement) | 🔴 n/a hors UE | 🔴 idem | Hébergeur équivalent local (R4, éval. fournisseurs) |
| Interopérabilité (HL7/FHIR) | ✅ mapping FHIR + HL7 v2.5 | ✅ **serveur HAPI JPA réel** R4 validation REQUIRE + relais RBAC (v0.4) | Profils nationaux IOP CI (v1.0) |
| Observabilité | 🟠 Prometheus/Grafana | ✅ **OTel collector + spans normés** (v0.4) | Sampling intelligent + métriques métier OTel (v1.0) |
| Infra GPU | 🔴 absente | ✅ **K8s GPU time-slicing ×2 + HPA** (v0.4) + **GHCR + NetworkPolicy + staging/prod** (v0.15) | Alignement des labels pods ↔ NetworkPolicy au déploiement réel CHU (R6) |
| Explicabilité IA | ✅ importance modalités | ✅ idem | Éval. clinique des sorties IA (R5-R7) |
| Dérive de modèles | 🟠 DAG Airflow drift-check | 🟠 idem | Seuils calibrés données CHU réelles (RM-05) |

**Conclusion (inchangée, renforcée)** : le socle technique est conforme
« by design » et désormais **observable de bout en bout** (imagerie STOW→OHIF,
référentiel FHIR HAPI, traces OTel, GPU orchestré) ; la conformité juridique
est un processus planifié (plan R1-R9 datés, `08-plan-validation-v1.0.0.md`).
« La certification est le produit » — aucune mise en production clinique sans
marquage CE.
