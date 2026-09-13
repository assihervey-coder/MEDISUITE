# Dossier technique de marquage CE — MEDISUITE (MDR 2017/745, classe IIb)

> **Statut : dossier EN CONSTRUCTION — jalon v1.0.0.** Chaque section porte un
> état (🟢 rédigé / 🟠 partiel / 🔴 à produire) et ses entrées/sorties. Ce
> dossier n'est pas une déclaration de conformité : aucune utilisation
> clinique avant consultation d'organisme notifié (voir
> `08-plan-validation-v1.0.0.md`).

## Cartographie du dossier (MDR Annexe II « informations techniques » + Annexe III « PMS »)

| § | Document MDR exigé | Fichier | État |
|---|---|---|---|
| 0 | Finalité du dispositif | `intended-purpose.md` (v0.1) | 🟢 |
| 1 | Identification du dispositif (Annexe II §1.1) + UDI | `01-identification-classification.md` | 🟠 |
| 1b | Classification (Annexe VIII, règle 11) | `01-identification-classification.md` | 🟠 |
| 2 | Informations à fournir à l'utilisateur (IFU, étiquetage) | `intended-purpose.md` + `ifu/` (4 profils + étiquetage UDI, v0.5) | 🟠 IFU rédigées, à valider usabilité |
| 3 | Conception & fabrication (spécifications, SPP) | `02-gspr-annexe-I.md` | 🟠 |
| 4 | Exigences générales de sécurité et de performance (EGSP, Annexe I) | `02-gspr-annexe-I.md` | 🟠 |
| 5 | Gestion des risques (ISO 14971, Annexe I §3) | `03-analyse-risques-iso14971.md` | 🟠 |
| 6 | Vérification & validation (IEC 62304, 81001-5-1) | `04-iec-62304-classe-C.md` | 🟠 |
| 7 | Ingénierie d'usage (IEC 62366-1) | `05-iec-62366-usabilite.md` | 🔴 |
| 8 | Évaluation clinique (Annexe XIV) + investigation (Annexe XV) | `06-evaluation-clinique.md` | 🔴 |
| 9 | Surveillance après commercialisation & vigilance | `07-pms-vigilance.md` | 🔴 |
| 10 | SMQ (ISO 13485) — preuves de processus | `../smq/` (8 procédures PROC-01…08, v0.5) | 🟠 rédigées, audit interne 🔴 |
| 11 | Plan de mise en conformité, jalons v1.0.0 | `08-plan-validation-v1.0.0.md` | 🟢 |

## Traçabilité avec le dépôt

- **Preuves techniques** : 373+ tests automatisés (packages, services,
  fusion IA), 21+ ADR (`docs/adr/`), audit d'écart `compliance/GAP-ANALYSIS.md`.
- **Écarts connus** : la GAP-ANALYSIS distingue explicitement ce qui est
  implémenté, documenté-à-exécuter et manquant — elle alimente directement
  les sections 🔴.
- **Règle d'or** (issue de l'audit v0.1) : *« la certification est le
  produit »* — chaque commit du dépôt est une preuve du dossier.

## Processus de revue

Toute modification du dispositif qui change la finalité, la classification,
la stack de calcul IA (v0.2 : backends torch/MONAI) ou les flux de données
est une **modification substantielle** au sens MDR art. 2(109) : révision
des sections 1, 3-5 et évaluation d'impact clinique (section 8) obligatoire
avant déploiement.
