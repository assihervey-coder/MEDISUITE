# EVOLUTION_POLICY — principes

1. **NO DIRECT CHANGE** : aucun changement de production sans proposition enregistrée.
   Le control plane n'est pas une formalité : c'est le seul chemin.
2. **Le control plane ne remplace pas MEDISUITE** — il décide, analyse, contrôle ;
   la plateforme existante exécute (39 services).
3. **Preuve par défaut** : chaque étape produit un artefact (impact, risque, diff,
   approbation, tests, compatibilité, monitoring, acceptation) rangé dans `evidence/`.
4. **Rollback préparé avant déploiement** — pas de release sans checkpoints complets.
5. **Honnêteté des statuts** : 🟢 prouvé / 🟠 partiel / 🔴 verrouillé terrain,
   aligné sur docs/COUVERTURE-ARBRE-INITIAL.md et les model-cards.
6. **Idempotence** : tout verrou automatisé (tests, --check) doit être reproductible CI.
