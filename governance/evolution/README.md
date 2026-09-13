# Politiques d'évolution

Le cycle d'évolution de MEDISUITE est **contrôlé de bout en bout**. Chaque document
de ce dossier est une politique normative ; les configs machine correspondantes
vivent dans `evolution-control-plane/config/` et sont appliquées par le code.

| Politique | Objet | Config machine |
|---|---|---|
| EVOLUTION_GOVERNANCE | rôles, instances, escrow de décision | approval-matrix.yaml |
| EVOLUTION_LIFECYCLE | machine à états complète | (code : domain/proposal/policies.py) |
| EVOLUTION_POLICY | principes généraux + NO DIRECT CHANGE | evolution.yaml |
| CHANGE_CLASSIFICATION | classes P0-P9 | change-types.yaml |
| APPROVAL_POLICY | qui approuve quoi | approval-matrix.yaml |
| ROLLBACK_POLICY | checkpoints + déclencheurs | rollback-policies.yaml |
| COMPATIBILITY_POLICY | contrats non-cassables | compatibility-policies.yaml |
| CLINICAL_CHANGE_POLICY | changements cliniques (P7/P8) | clinical PROPOSAL template |
| AI_CHANGE_POLICY | lineage IA obligatoire | ai PROPOSAL template |
| DATA_CHANGE_POLICY | migrations EXPAND→CONTRACT | data PROPOSAL template |
| SECURITY_CHANGE_POLICY | changements sécurité (P8) | security PROPOSAL template |
| REGULATORY_CHANGE_POLICY | impact MDR (P9) | regulatory PROPOSAL template |
