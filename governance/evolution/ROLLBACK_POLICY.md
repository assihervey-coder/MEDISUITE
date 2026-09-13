# ROLLBACK_POLICY

**Le rollback est préparé avant le déploiement.** Une release sans checkpoints
complets est refusée par le rollout-engine.

## Checkpoints obligatoires (7)
version précédente · checkpoint DB · snapshot de configuration · versions de modèles ·
état des feature flags · manifeste de déploiement · snapshot de preuves.

## Déclencheurs
error_rate > 1 % (5 min) · p95 > 2 s (10 min) · alerte sûreté clinique (immédiat) ·
drift modèle PSI > 0.2 · chute de débit > 20 % · alerte critique · décision humaine.

## Exécution
1. gel du rollout ; 2. restauration checkpoints (flags → OFF d'abord) ;
3. smoke post-rollback bloquant ; 4. preuve `RBK-*` + `EVD-*` ; 5. incident post-mortem.
V1 sans Kubernetes temps réel : les déclencheurs sont évalués par `engines/rollout-engine`
sur les métriques fournies (Prometheus), l'exécution reste humaine outillée.
