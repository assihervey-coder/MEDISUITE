# PROC-05 — Achats et évaluation des fournisseurs (ISO 13485 §7.4)

**Propriétaire** : Ingénierie + RQ | **Revue** : annuelle | **Version** : 1.0

## 1. Finalité

Maîtriser le risque de la chaîne d'approvisionnement **logicielle** :
MEDISUITE intègre des composants tiers (PACS Orthanc, HAPI FHIR, runtime
NVIDIA, bibliothèques IA, hébergement) dont la défaillance est un risque
patient direct (RM-06, RM-07).

## 2. Grille d'évaluation (score 1-4 par critère, approbation ≥ moyenne 3)

| Critère | Question type | Preuves acceptées |
|---|---|---|
| Conformité standard | le composant implémente-t-il la norme citée ? | tests d'interopérabilité du dépôt (HL7, DICOMweb, FHIR R4) |
| Sécurité | politique CVE, délais de correctif, SBOM disponible | CVE historique, releases de sécurité |
| Maintenabilité | activité du projet, gouvernance, licence | commits, fondation, LICENCE (GPL-3 Orthanc : implications intégration documentées) |
| Pérennité CI | disponibilité locale, absence de dépendance cloud bloquante | déploiement offline testé |
| Traçabilité | versions épinglées, chaîne d'approvisionnement reproductible | compose/K8s épinglés, DVC, MLflow |

## 3. Fournisseurs critiques (liste initiale — à tenir à jour)

| Fournisseur | Composant | Statut v0.5 |
|---|---|---|
| Orthanc Team | PACS + DICOMweb | évalué techniquement (compose réel) ; grille formelle à compléter |
| HAPI/University Health Network | serveur FHIR R4 | idem |
| NVIDIA | drivers + device plugin + CUDA | 🔴 accès matériel requis (CHU) |
| Hébergeur CI | datacenter | 🔴 sélection en cours (critère équivalent HDS) |
| PyTorch / MONAI / NumPy | inférence IA | SBOM à générer (jalon R4) |

## 4. Réévaluation et sorties

- Réévaluation **annuelle** ou à chaque montée de version majeure du composant.
- Un fournisseur dégradé (< 3) : plan d'action (version épinglée, fork,
  alternative) consigné + impact FMEA.
- Enregistrements : grilles remplies, décisions d'approbation, suivi CVE.
