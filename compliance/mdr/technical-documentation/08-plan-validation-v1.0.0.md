# §10 — Plan de mise en conformité v1.0.0 (marquage CE MDR IIb)

> Feuille de route consolidée — mise à jour à chaque release. Principe issu
> de l'audit v0.1 : **« la certification est le produit »** — le plan combine
> jalons techniques (v0.2-v0.4 : livrés) et jalons réglementaires (v1.0).

## 1. Historique des jalons techniques (livrés, tags Git)

| Jalon | Contenu | Preuve |
|---|---|---|
| v0.1.0 | noyau + 90 scores cliniques + 38 services + fusion IA + MLOps + infra GitOps | 373 tests verts, 8 commits |
| v0.2.0 | écrans BI-RADS/code AVC, backends torch/MONAI (ADR 0022), PACS Orthanc réel | 31/31 tests IA, 12/12 imaging |
| v0.3.0 | OHIF v3 sur /dicom-web, fusion torch ENTRAÎNABLE (ADR 0023) | 16 tests torch fusion, chaîne STOW→OHIF |
| v0.4.0 | HAPI FHIR R4 réel, OTel stdlib + collector, K8s GPU time-slicing | 12/12 integration, 81/81 packages |
| v0.5.0 | R1-R4 : SMQ 8 procédures, IFU 4 profils, usabilité formative, Vault/mTLS/SBOM/pentest-plan, ADR-0024 profils IOP-CI, banc perf EGSP | 15/15 integration, 81/81 packages |

## 2. Jalons réglementaires restants (vers v1.0.0)

| # | Livrable | Section dossier | Priorité | Estimation |
|---|---|---|---|---|
| R1 | SMQ ISO 13485 : cartographie processus, procédures documentées (libération, incidents, qualité fournisseurs) | `../smq/` PROC-01…08 ✅ rédigées v0.5 | haute — **audit interne + auditeur externe 🔴** | M+0 → M+4 |
| R2 | IFU complètes (4 profils) + étiquetage + UDI/EID (GS1) | `ifu/` ✅ rédigées v0.5 | haute — **UDI-EID émission + écran À propos 🔴** | M+1 → M+3 |
| R3 | Usabilité formative (IEC 62366) | `usability/` protocole + grilles ✅ prêts v0.5 | haute — **exécution avec participants CHU 🔴** | M+2 → M+6 |
| R4 | Durcissement : Vault/mTLS/SBOM + pentest + banc perf | `security/hardening/` + `tools/bench/` ✅ outillage v0.5 | haute — **exécution pentest externe + campagne GPU CHU 🔴** | M+1 → M+5 |
| R5 | Protocole investigation multicentrique + accords CHU + comité d'éthique | `06-evaluation-clinique.md` | critique | M+2 → M+6 |
| R6 | Exécution investigation (inclusions, monitoring DSMB) | Annexe XV | critique | M+6 → M+18 |
| R7 | Rapport évaluation clinique (MEDDEV 2.7/1 rev 4) + bénéfice-risque final | Annexe XIV | critique | M+18 → M+21 |
| R8 | Dossier notifié (EUDAMED) + audit organisme notifié + certification | art. 52-54 | critique | M+21 → M+30+ |
| R9 | PMS/vigilance opérationnels (registre incidents, PSUR, PMCF) | `07-pms-vigilance.md` | haute | M+3 → M+8 |

## 3. Critères de passage en usage clinique contrôlé (avant CE)

Aucune utilisation clinique réelle avant certification, SAUF cadre pilote de
recherche validé par comité d'éthique (R5). Critères d'entrée pilote :
1. R1-R4 clôturés (SMQ minimum viable, IFU, usabilité formative+summative,
   sécurité durcie) ;
2. FMEA résiduelle : aucun risque ≥12 sans mesure close ;
3. Télémétrie OTel + audit actifs sur site pilote ;
4. formation documentée des utilisateurs pilotes.

## 4. Gouvernance

- **Comité de gestion des risques** (qualité, ingénierie, clinicien CHU,
  juridique RGPD) — mandat 🔴 à rédiger (R1).
- **DSMB** pour l'investigation multicentrique (R6).
- **Responsable réglementaire** (RC) désigné pour EUDAMED et vigilance (R8).

## 5. Risques du plan (croisement avec audit R1-R10)

Les risques projet de l'audit (adoption utilisateurs, chiffrage 2,4-25 M€
selon scénario, dépendance single-maintainer…) restent la principale menace
d'échéance ; l'arbitrage scénario S2 (8-12 M€ / 36 mois) est le référentiel
de capacité assumé pour ce calendrier. La v0.4.0 démontre la faisabilité
technique (HAPI, OTel, GPU) — la charge restante est essentiellement
documentaire et clinique.
