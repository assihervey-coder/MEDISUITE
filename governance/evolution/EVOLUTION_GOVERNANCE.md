# EVOLUTION_GOVERNANCE

## Instances
1. **Comité d'évolution** — décide P8/P9, arbitre les blocages (clinical_lead,
   safety_officer, regulatory_affairs, security_officer, maintainer).
2. **Approvers désignés** — par classe dans `approval-matrix.yaml`.
3. **Mainteneur d'exécution** — opère le control plane, ne peut PAS s'auto-approuver.

## Principes
- Toute décision est **tracée** (événement d'audit chaîné + preuve EVD-*).
- Séparation des devoirs : l'auteur d'une proposition n'est jamais son approbateur.
- Une approbation sans dossier de preuve complet est **nulle**.
- Les délégations de signature (ISO 14155 §registre investigateurs) s'appliquent
  aux validations cliniques : un délégué signe dans la limite de sa délégation datée.

## Escalade
Blocage > 10 jours ouvrés sur DECISION_PENDING → escalade comité (enregistrée).
Conflit sûreté vs délai : la sûreté gagne toujours (voir CLINICAL_CHANGE_POLICY).
