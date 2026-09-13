# §1 — Identification et classification du dispositif (MDR Annexe II §1.1, Annexe VIII)

## 1. Identification du dispositif

| Champ | Valeur |
|---|---|
| Dénomination commerciale | MEDISUITE |
| Dénomination générique | Plateforme logicielle d'aide à la décision clinique par fusion multimodale |
| Fabricant | ASSI Herve (concepteur-éditeur), Abidjan, Côte d'Ivoire |
| Modèle de distribution | logiciel installé dans l'établissement de santé (on-premises / cloud privé HDS-équivalent) |
| Version visée par ce dossier | v1.0.0 (jalons v0.1→v0.4 documentés par tags Git et ADR) |
| UDI-EID | à attribuer par une agence émettrice (GS1 recommandée) — 🔴 v1.0 |
| Basic UDI-DI | à définir par famille : `MEDISUITE-PLTF-AIDE-DECISION` — 🟠 |
| EMDN | V20199999 (Software in-vitro) / à affiner V20 logiciel d'imagerie et d'aide décisionnelle |
| GMDN / catégorie | 60010 Software, clinical decision support |
| Système | serveur applicatif, Docker/Kubernetes, PostgreSQL/SQLite, Orthanc PACS, HAPI FHIR R4 |
| Sites de fabrication | Abidjan (développement), pas de fabrication physique |

## 2. Combinaison avec d'autres dispositifs

MEDISUITE fonctionne avec : des modalités d'imagerie DICOM conformes PS3.x
(acquisition hors dispositif MEDISUITE), des automates de laboratoire via
HL7 v2.5, des serveurs PACS (Orthanc OSS) et des référentiels FHIR R4
(HAPI). Aucune combinaison avec un médicament. Le dispositif n'administre
pas d'énergie et n'a pas de contact physique avec le patient : classe
« dispositif non invasif, logiciel ».

## 3. Classification — Annexe VIII, **règle 11**

MEDISUITE est un **logiciel destiné à fournir des informations utilisées
pour prendre des décisions à des fins de diagnostic ou de thérapeutique**
(specific rule 11 : « Software intended to provide information which is used
to take decisions with diagnosis or therapeutic purposes ») → classe IIb.

### Justification règle par règle

| Règle | Applicabilité | Conclusion |
|---|---|---|
| 1-8 (invasivité, source d'énergie, substances) | non — aucun contact corps/énergie | n/a |
| 9-10 (thérapeutique active) | non — pas d'administration d'énergie | n/a |
| **11 (logiciel CDS)** | **oui** | **IIb** |
| 11 §2 (simple recherche d'informations) | partiel : viewer DICOM/OHIF seul = IIa | segment IIa isolé non commercialisé séparément |
| 22 (site informatique de surveillance) | non — pas de surveillance continue vitale | n/a |

### Sévérité des décisions influencées (justification IIb, pas IIa)

Des sorties MEDISUITE peuvent être utilisées pour des décisions **susceptibles
de causer la mort ou une détérioration irréversible de l'état de santé** :
priorisation trauma/AVC (fenêtres rtPA ≤4,5 h, thrombectomie), détection
BI-RADS 4-6, ASPECTS <7. Même si la décision finale reste humaine (le
dispositif n'est pas autonome), l'Annexe VIII impose IIb pour ces usages.
Choix prudent : **l'ensemble de la plateforme est traitée IIb** (ADR-0004),
une segmentation IIa par module étant rejetée pour éviter un contournement
réglementaire et une fragmentation du SMQ.

### Ce qui exclut le dispositif du champ MDR

Les fonctions administratives (facturation DFT, annuaire, portail patient
consentements RGPD) ne fournissent pas d'information médicale individuelle :
elles sont **hors dispositif médical** et sont tracées comme composants de
l'IT hospitalier — frontière documentée module par module dans
`docs/MODULES.md`, à consolider dans le rapport de classification final 🔴.

## 4. Variantes et configurations

- **MEDISUITE Complete** (38 services, K8s GPU) — configuration de référence.
- **MEDISUITE Core** (5 services cœur + PACS + OHIF) — CHU de taille moyenne.
- Variantes linguistiques (fr/en) sans impact performance/sécurité.
- Toute variante IA (modèle entraîné) constitue une configuration à
  qualifier séparément (section 8 — libération de modèle).
