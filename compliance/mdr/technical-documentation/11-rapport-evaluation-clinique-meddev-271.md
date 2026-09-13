# TD-11 — Rapport d'évaluation clinique (CER) — structure MEDDEV 2.7/1 rev 4

> **Statut (v0.9.0) : squelette normatif 🟢 — CONTENU 🔴 jusqu'à R7 (M+21).**
> Ce document fixe la structure du rapport d'évaluation clinique exigé par
> l'**Annexe XIV MDR 2017/745** et le format **MEDDEV 2.7/1 rev 4**, conformément
> à l'**ADR-0026**. Chaque section mappe : l'exigence, la **source de données
> réelle du dépôt**, et l'état. Aucun chiffre n'est pré-écrit : les données
> d'investigation n'existent pas avant l'exécution R6-R8 (honnêteté
> réglementaire — la validité clinique des sorties IA reste 🔴 jusqu'à R6-R8).
>
> **Objet évalué** : plateforme MEDISUITE (aide à la décision clinique
> multimodale IA) — classe IIb, règle 11 Annexe VIII, prétention clinique
> S1-S5 du protocole TD-10 (MEDISUITE-CI-01).

## Section 0 — Résumé exécutif

| Exigence MEDDEV | Source | État |
|---|---|---|
| Titre, identifiants (Basic UDI-DI, version), fabricant | `01-identification-classification.md` + `labeling.json` (api-gateway) | 🟢 mappé |
| Synthèse de l'évaluation + conclusion bénéfice-risque | **à rédiger en R7** à partir des sections 1-9 | 🔴 |
| Prétention clinique évaluée | TD-10 §prétention S1-S5 (`10-protocole-…R5.md`) | 🟢 mappé |
| Profil de l'évaluateur clinique + CV signé | à désigner (promoteur) — exigence MEDDEV §8 | 🔴 |

## Section 1 — Portée de l'évaluation clinique

| Exigence | Source | État |
|---|---|---|
| Finalité, indications, populations cibles | `intended-purpose.md` + IFU (4 profils, v0.5) | 🟢 mappé |
| Prétentions cliniques S1-S5 (AVC, sepsis, polytrauma, pédiatrie, mobile) | TD-10 §2 — endpoints co-primaires (κ pondéré ≥ 0,80 IC95 inf > 0,72 ; sûreté 30 j ; délais ≥ −10 %) | 🟢 mappé |
| Contexte d'usage ivoirien (ressources limitées, offline) | `docs/OFFLINE-PORTAL.md` + écran About (UDI) | 🟢 mappé |

## Section 2 — Description du dispositif et de ses applications cliniques

| Exigence | Source | État |
|---|---|---|
| Architecture, modules 26, fusion IA (ADR-0016/0017/0022/0023) | `docs/MODULES.md` + `docs/audit-26-modules.md` | 🟢 mappé |
| Spécifications / SPP | `02-gspr-annexe-I.md` | 🟠 à compléter R8 |
| Versions logicielles couvertes par l'évaluation | eCRF : `MEDISUITE_VERSION` sur /health (38 services) + étiquetage §2.1 | 🟢 mappé |

## Section 3 — Données d'investigation clinique (cœur du CER)

| Exigence | Source | État |
|---|---|---|
| Protocole conforme ISO 14155 / Annexe XV | TD-10 (MEDISUITE-CI-01) | 🟠 rédigé — signatures/soumissions 🔴 (`compliance/mdr/clinical/signatures/`, `compliance/mdr/submissions/`) |
| Données brutes post-verrou M+18 | **GET /api/v1/ecrf/extract (SAF)** — data manager, checksum figé, alarme intégrité | 🔴 exécution R6 |
| Analyse SAP + rapport statistique | annexe A5 du protocole (statisticien contractuel indépendant) | 🔴 R7 |
| Adjudication indépendante (κ ≥ 0,75) | comité aveugle, F05 eCRF | 🔴 R6-R7 |
| Conformité monitoring (visites A4, SDV 20 %/100 % SAE, déviations) | `compliance/mdr/clinical/monitoring/` | 🟠 instruments prêts — exécution 🔴 |
| Déviations et leur impact sur la validité | `registre-deviations.md` (condition de lock : déviations majeures résolues) | 🔴 R6 |
| Avis DSMB (règles d'arrêt, ≥ 2 SAE/site) | export DSMB v0.7 + procès-verbaux à produire | 🔴 R6-R7 |

## Section 4 — État de l'art

| Exigence | Source | État |
|---|---|---|
| Revue de littérature reproductible (requêtes, dates, critères) | **à produire R7** — PubMed + African Journals Online ; log de recherche en annexe du CER (ADR-0026 §3) | 🔴 |
| Benchmarks des scores implémentés (BI-RADS, NIHSS, ASPECTS, qSOFA, Wells…) | `packages/clinical-rules` (référentiels cités) + `docs/BENCHMARK-GPU.md` | 🟢 mappé |
| Pratiques d'aide à la décision en contextes de ressources limitées | littérature R7 | 🔴 |

## Section 5 — Équivalence (non revendiquée)

| Exigence | Source | État |
|---|---|---|
| Pas de dispositif équivalent déclaré — performance démontrée par l'investigation propre | ADR-0026 §5 (décision) | 🟢 tranché |
| (Si revendication ultérieure) annexe A5.2 MEDDEV intégralement | — | n/a |

## Section 6 — Analyse des données disponibles (bénéfice-risque)

| Exigence | Source | État |
|---|---|---|
| Synthèse des résultats vs endpoints co-primaires | rapport SAP R7 → à rédiger | 🔴 |
| Sûreté : EI/SAE liés au dispositif, règle d'arrêt ≥ 2 SAE/site | eCRF F04-SUIVI30J + DSMB | 🔴 R6 |
| Gestion des risques résiduelle | `03-analyse-risques-iso14971.md` (RM-01…RM-10, RPN post-investigation) | 🟠 à actualiser R7 |
| Bénéfice-risque final (Annexe I §8/§23) | **conclusion du CER R7** | 🔴 |

## Section 7 — Limites et facteurs humains

| Exigence | Source | État |
|---|---|---|
| Limites assumées (modalités manquantes ADR-0018, hors-ligne, rural) | IFU + `docs/K8S-GPU.md` + protocole §limites | 🟢 mappé |
| Ingénierie d'usage : formative + sommative (≥ 15 participants, 5 scénarios critiques) | `05-iec-62366-usabilite.md` + `usability/` (R3) | 🔴 exécution terrain |
| Automation bias / sur-dépendance à l'IA | protocole R3 (grille passation) + IFU avertissements | 🟠 rédigé — validation 🔴 |

## Section 8 — Évaluation de la prétention clinique

| Exigence | Source | État |
|---|---|---|
| Concordance prétention ↔ endpoints ↔ résultats | TD-10 §2 + rapport SAP | 🔴 R7 |
| Performance par site et par scénario (COC/TRI/YOP/BOU) | SAF (derivees SAP) → tables du CER (gabarits annexe A5 du protocole) | 🔴 R7 |
| Validité clinique des sorties IA | **dépend entièrement de R6-R8 — reste 🔴 par conception** | 🔴 |

## Section 9 — Conclusion + mise à jour (PMCF)

| Exigence | Source | État |
|---|---|---|
| Conclusion sur conformité EGSP et bénéfice-risque | CER R7 | 🔴 |
| Plan PMCF (IIb : mise à jour ≥ annuelle) + vigilance art. 87-90 | `07-pms-vigilance.md` | 🟠 rédigé — exécution post-certification 🔴 |
| Traçabilité CER ↔ EGSP ↔ risques | protocole annexe A6 (mapping) | 🟢 mappé |

## Registre des révisions du CER (à tenir après R7)

| Version | Date | Auteur | Motif | Validé par |
|---|---|---|---|---|
| 0.1-squelette | 2026-09-14 | ingénierie (v0.9.0) | structure MEDDEV 2.7/1 rev 4 (ADR-0026) | 🔴 revue PROC-08 à faire |
| 1.0 | 🔴 M+21 | évaluateur clinique + statisticien | données R6-R8 | promoteur + revue direction |
