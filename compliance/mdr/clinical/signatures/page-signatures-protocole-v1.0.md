# Page de signatures du protocole — MEDISUITE-CI-01 v1.0

> **Objet** : page de signatures formelle du protocole d'investigation
> **MEDISUITE-CI-01 v1.0** (`10-protocole-investigation-multicentrique-R5.md`),
> exigée par **ISO 14155:2020 §4.8 / §6.6** (signature du protocole par
> l'investigateur coordonnateur, l'investigateur de chaque site et le
> promoteur) et **MDR 2017/745 Annexe XV chapitre I**.
>
> **Statut (v0.9.0) : 🟢 instrument prêt — signatures 🔴 terrain (jalon R5,
> M+2 → M+6).** Un exemplaire signé (PDF scanné) est archivé dans le dossier
> d'investigation (rétention 25 ans, art. MDR 10.8) et joint au paquet
> ANOC-CI (`compliance/mdr/submissions/checklist-ANOC-CI.md` — item
> « protocole signé »). Aucune inclusion avant toutes les signatures.

## 1. Signatures de version (protocole v1.0)

Chaque signataire confirme : avoir lu et approuvé l'intégralité du protocole
v1.0 et ses annexes A1-A6 ; s'engager à l'exécuter tel quel ; déclarer les
conflits d'intérêts (formulaire annexe) ; comprendre que toute modification
passe par un amendement versionné (voir §3) approuvé avant application.

| # | Rôle | Nom | Institution | Signature | Date | CI (déclaration conflits) |
|---|---|---|---|---|---|---|
| 1 | Promoteur / fabricant | ASSI Herve | MEDISUITE | 🔴 | — | 🔴 jointe |
| 2 | Investigateur coordonnateur | 🔴 à nommer | CHU de Cocody | 🔴 | — | 🔴 |
| 3 | Responsable réglementaire (RC) | 🔴 à désigner | MEDISUITE | 🔴 | — | 🔴 |
| 4 | Statisticien (SAP, indépendant) | 🔴 à contractualiser | 🔴 (contrat) | 🔴 | — | 🔴 |
| 5 | Data manager | 🔴 à désigner | MEDISUITE | 🔴 | — | 🔴 |
| 6 | Président DSMB | 🔴 à désigner (indépendant, §5.9) | 🔴 | 🔴 | — | 🔴 |
| 7 | Responsable monitoring (moniteur principal) | 🔴 (contrat) | 🔴 | 🔴 | — | 🔴 |

## 2. Règles d'exécution liées aux signatures

1. **Blocage d'inclusion** : un site ne peut inclure son premier sujet qu'après
   (a) signature de son investigateur (§3), (b) avis favorable ANOC-CI,
   (c) autorisation Ministère, (d) enregistrement PACTR, (e) accord de site
   signé — la chaîne complète est pilotée dans
   `compliance/mdr/submissions/00-index-soumissions.md`.
2. **Signature électronique eCRF ≠ signature du protocole** : la signature
   d'entrée eCRF (verrou ISO 14155 §4.8, service eCRF) porte sur les
   *données* ; la présente page porte sur le *protocole*. Les deux sont
   exigées, aucune ne remplace l'autre.
3. **Diffusion** : version signée distribuée à tous les investigateurs et au
   moniteur ; la version électronique de référence est ce dépôt Git (tag de
   la release) — l'exemplaire signé porte le tag Git correspondant
   (étiquetage §2.1 du protocole).

## 3. Amendements

Tout amendement reçoit un numéro séquentiel (A1, A2…), une version de
protocole (1.1, 2.0…), est approuvé par ANOC-CI **avant application**
(sauf mesure urgente de sûreté des sujets, à notifier immédiatement), et
re-signé selon le registre des investigateurs
(`registre-investigateurs.md`).

| Amendement | Version protocole | Objet (résumé) | Approuvé ANOC-CI le | Signatures complétées le |
|---|---|---|---|---|
| A1 | 🔴 | — | — | — |

## 4. Fin d'investigation

À la clôture (fin du suivi 30 j du dernier sujet, avant le verrou M+18), le
coordonnateur et le promoteur signent le **rapport de fin d'investigation**,
prérequis documenté du verrou de base (`study/status` → `study/lock`) et de
l'analyse SAP alimentant le CER MEDDEV 2.7/1 (TD-11, ADR-0026).
