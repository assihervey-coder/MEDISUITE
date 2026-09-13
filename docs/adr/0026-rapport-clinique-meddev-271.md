# ADR-0026 — Rapport d'évaluation clinique MEDDEV 2.7/1 rev 4 (jalon R7)

**Statut** : accepté (structure & pipeline — v0.9) · **Date** : 2026-09-14 ·
**Décideurs** : ingénierie + affaires réglementaires
**Supersede** : complète ADR-0004 (classification MDR) et TD-06 (évaluation
clinique — plan) ; le *contenu* du rapport reste 🔴 jusqu'à la fin de R6-R8.

## Contexte

La v0.8.0 clôt la chaîne *outillage* de l'investigation MEDISUITE-CI-01 :
eCRF opérationnel (v0.7), monitoring A4 + verrou de base M+18 + extraction
SAF du data manager (v0.8). Reste la question du **livrable terminal** que
cette chaîne alimente : le rapport d'évaluation clinique (CER) exigé par
l'**Annexe XIV MDR 2017/745** et structuré par **MEDDEV 2.7/1 rev 4**,
jalon **R7 (M+18 → M+21)** du plan de validation v1.0.0.

Trois constats motivent une décision d'architecture *maintenant* :

1. **Le CER est un produit de données, pas une prose** : son chapitre
   central (analyse des données d'investigation) ne peut être écrit qu'à
   partir de l'extraction SAF post-verrou. Si le pipeline
   eCRF → lock → SAF → SAP → CER n'est pas arrêté à l'avance, l'analyse
   de R7 deviendra une réécriture a posteriori — exactement ce que les
   auditeurs notifiés traquent (données retravaillées sans traçabilité).
2. **Le format MEDDEV 2.7/1 rev 4 est une structure normative stricte**
   (sections 0 à 9, littérature documentée par requêtes reproductibles,
   équivalence justifiée ou écartée) — il vaut mieux que le squelette
   existe AVANT les données, pour que chaque donnée produite en R6
   s'insère dans sa case.
3. **La validité clinique des sorties IA est 🔴 jusqu'à R6-R8** (entériné) :
   le CER est précisément le document qui transformera les agrégats
   DSMB/extraction en preuve de performance clinique — ou en constat
   d'échec. L'architecture doit donc être honnête sur ce qui est
   *prêt* (structure, sources, pipeline) et ce qui est *à prouver*.

## Décision

**Le CER de MEDISUITE-CI-01 sera rédigé selon MEDDEV 2.7/1 rev 4, alimenté
uniquement par des sources versionnées du dépôt, avec un squelette
normatif créé dès maintenant (TD-11) et rempli en R7 après le verrou M+18.**

1. **Pipeline de données (une seule direction, zéro réécriture)** :
   ```
   eCRF (R6, saisie signée + SDV) → VERROU M+18 (irréversible)
     → GET /extract (SAF, data manager, alarme intégrité)
     → analyse SAP (statisticien contractuel, annexe A5 du protocole)
     → adjudication (comité aveugle κ≥0,75)
     → CER MEDDEV 2.7/1 (TD-11, R7) → bénéfice-risque final (TD-03)
   ```
   Chaque flèche est déjà outillée : `/study/lock` + `/extract`
   (v0.8), agrégats DSMB (v0.7), registre de déviations (v0.8).
2. **Squelette normatif = TD-11**
   (`compliance/mdr/technical-documentation/11-rapport-evaluation-clinique-meddev-271.md`)
   — les 9 sections MEDDEV, chacune mappée à sa source de données réelle
   du dépôt, avec état 🟢 (structure prête) / 🔴 (contenu attendu R7).
3. **État de l'art (section 8 MEDDEV)** : recherche de littérature
   documentée par requêtes reproductibles (PubMed/African Journals Online,
   date de coupure, critères d'inclusion/exclusion consignés en annexe du
   CER) — un CER dont la littérature n'est pas reproductible est
   irrecevable devant un notifié. Focus : imagerie diagnostique en
   contexte de ressources limitées, aide à la décision clinique
   informatisée, performance des scores implémentés (BI-RADS, NIHSS,
   ASPECTS, qSOFA…).
4. **Auteurs** : évaluateur clinique désigné par le promoteur + CV en
   annexe (exigence MEDDEV §8) ; le statisticien SAP est contractuel et
   indépendant du développement (déjà acté au protocole §11) ; l'avis du
   DSMB est annexé au CER (conflits d'intérêt déclarés).
5. **Équivalence** : non revendiquée (pas de dispositif équivalent
   déclaré) — la performance est démontrée par l'investigation propre
   MEDISUITE-CI-01 ; toute tentative ultérieure d'équivalence devra
   satisfaire MEDDEV 2.7/1 annexe A5.2 intégralement.
6. **PMS/PMCF** : le CER R7 est l'état *initial* ; la mise à jour
   périodique post-certification suit le plan PMCF de TD-07 (IIb :
   mise à jour au moins annuelle) — le pipeline de données est le même,
   alimenté par les données de surveillance au lieu de l'investigation.

## Alternatives écartées

- **CER fondé sur la littérature seule** (parcours MEDDEV « literature
  based ») : recevable pour certains IIa, **pas pour une prétention
  clinique S1-S5 d'un IIb aide au diagnostic** — le notifié exigera des
  données d'investigation propres (Annexe XIV §1.1a).
- **Rédiger le CER à partir d'un pilote interne sans verrou** : violerait
  le protocole §7.4 (analyse sur base gelée uniquement) et produirait une
  preuve contestable devant l'ANOC-CI comme devant le notifié.
- **Attendre R8 pour structurer le CER** : le rapport est l'entrée du
  dossier notifié ; structurer tard = découvrir les trous de données
  après la fin de l'investigation, sans possibilité d'y remédier.

## Conséquences

- **🟢 livré en v0.9** : ADR-0026, squelette TD-11 mappé aux sources,
  écran promoteur affichant la phase R7 (verrou → analyse → rapport).
- **🔴 reste à produire (terrain, daté)** : données R6 (inclusions,
  monitoring, adjudication), verrou M+18 réel, analyse SAP, littérature
  documentée, CER final (M+21) puis mises à jour PMCF annuelles.
- Le squelette TD-11 est auditable dès maintenant par revue interne
  (PROC-08) : toute section qui n'aurait pas de source de données réelle
  identifiée doit être corrigée AVANT le démarrage de R6.
