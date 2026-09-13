# AI_CHANGE_POLICY

Une évolution IA n'est JAMAIS « model.pth → production ». Chaîne obligatoire :
Dataset → Preprocessing → Training → Model → Evaluation → Calibration →
Clinical Validation → Risk Assessment → Approval → Deployment → Monitoring.

**Lineage complet exigé** (template AI_PROPOSAL.yaml) : model_id/version/checksum,
dataset_id/version, preprocessing, prompt, retrieval, evidence, clinical_rules,
threshold, calibration, safety_policy — chaque maillon versionné.

- Classe plancher P6 ; changement de seuil décisionnel ou de politique de sûreté → P8.
- Métriques de performance : verrouillées jusqu'aux runs terrain R6-R8 / lock M+18
  (model-cards = source de vérité, idempotence CI).
- Abstention/OOD requise sur toute sortie décisionnelle ; drift monitoré (PSI/KS).
- Les runs R6 produisent les model-cards réelles (décision backlog : pas de codage anticipé).
