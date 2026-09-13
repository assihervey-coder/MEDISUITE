# PROC-01 — Maîtrise des documents et des enregistrements (ISO 13485 §4.2.4-4.2.5)

**Propriétaire** : Responsable qualité | **Revue** : annuelle | **Version** : 1.0 (2026-09)

## 1. Finalité

Garantir que tout document utilisé par MEDISUITE (procédures, ADR, specs,
IFU, configs de production) est **approuvé, identifiable et à jour**, et que
toute décision portant sur la sécurité ou la performance du dispositif reste
reconstructible des années plus tard — exigence du dossier technique MDR.

## 2. Typologie et canaux

| Type | Canal | Approbation | Immutabilité |
|---|---|---|---|
| Procédures SMQ, dossier CE, IFU | `compliance/` (Git) | RQ + direction | par PR + tag |
| Décisions d'architecture (ADR) | `docs/adr/` (Git) | développeur + revue par les pairs | immuable (supersession) |
| Code & tests | Git monorepo | CI verte (373+ tests) | historique Git |
| Configurations de production | `infrastructure/` | revue sécurité | par PR + GitOps |
| Enregistrements qualité | espace CHU + archive annuelle | RQ | non rétro-modifiable |
| Données d'entraînement IA | DVC + MLflow | comité de libération de modèle | versionné DVC |

## 3. Cycle de vie d'un document

1. **Création** : modèle type (finalité, champ, responsabilités, flux,
   enregistrements, indicateurs) ; ID unique `PROC-xx` / section dossier CE.
2. **Revue** : relecture croisée (rédacteur ≠ relecteur) ; commentaires
   tracés dans la PR.
3. **Approbation** : RQ pour les procédures ; direction pour la politique.
4. **Diffusion** : merge sur `main` = publication ; les versions déployées
   en CHU sont figées par tag de release.
5. **Revue périodique** : ≤ 12 mois — bannière « périmé » si dépassée.
6. **Obsolescence** : marquage « SUPERSEDED » avec lien vers le successeur
   (jamais de suppression) — même règle que les ADR.

## 4. Enregistrements — exigences

- Chaque procédure liste **explicitement** ses enregistrements (table
  cartographie de `00-index-smq.md`) : un enregistrement sans propriétaire
  est un écart.
- Conservation : durée de vie du dispositif **+ 2 ans**, minimum 10 ans pour
  les dossiers de lot/déploiement (MDR art. 10.8).
- Protection : chaîne d'audit SHA-256 pour les traces applicatives ;
  sauvegardes chiffrées pour l'archive qualité (contrôle mensuel d'intégrité).

## 5. Indicateurs

- % de documents à revue à jour (cible ≥ 95 % au premier audit interne).
- Délai moyen d'approbation d'un document ≤ 10 jours ouvrés.
- Zéro enregistrement qualité perdu lors des contrôles d'intégrité mensuels.
