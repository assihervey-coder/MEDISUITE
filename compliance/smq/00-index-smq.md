# SMQ MEDISUITE — Système de Management de la Qualité (ISO 13485:2016)

> Statut : procédures **rédigées v0.5, non auditées** — certification par
> organisme accrédité = jalon R1 du plan `../mdr/technical-documentation/08-plan-validation-v1.0.0.md`.

## Engagement de la direction (ISO 13485 §5.1)

Le fabricant s'engage à : maintenir l'efficacité du SMQ, porter la politique
qualité (zéro compromis sur la sécurité patient ; « la certification est le
produit »), fournir les ressources (revue de direction semestrielle),
nommer un **responsable qualité** indépendant du développement avant le
premier audit interne.

## Cartographie processus → procédures

| Processus | Procédure | Enregistrements produits |
|---|---|---|
| Maîtrise documentaire | `PROC-01-maitrise-documentaire.md` | liste des documents, historiques Git, revues datées |
| Gestion des risques | `PROC-02-gestion-risques.md` | plan de gestion, FMEA RM-*, rapports bénéfice-risque |
| Conception & V&V | `PROC-03-revue-conception-vnv.md` | comptes rendus de revues, plans/rapports de test |
| Incidents & CAPA | `PROC-04-incidents-capa.md` | registre incidents, fiches CAPA, preuves d'efficacité |
| Fournisseurs | `PROC-05-fournisseurs.md` | grille d'évaluation, décisions d'approbation |
| Formation & compétences | `PROC-06-formation-competences.md` | plan de formation, fiches d'habilitation |
| Libération (release) | `PROC-07-liberation-release.md` | checklist de libération signée, notes de version |
| Audit interne & revue de direction | `PROC-08-audit-interne-revue-direction.md` | rapports d'audit, PV de revue de direction |

## Règles communes (appliquées à toutes les procédures)

1. **Document = propriétaire nommé + fréquence de revue ≤ 12 mois** ; un
   document sans revue à date est « périmé » et marqué tel (bannière).
2. **Enregistrement = preuve datée et non rétro-modifiable** : les
   enregistrements qualité vivent hors Git (espace de partage CHU + archive
   annuelle figée), sauf ceux nativement immuables (chaîne d'audit
   `audit_chain`, tags Git, ADR).
3. **Priorité sécurité patient** : en cas de conflit calendrier/sécurité, la
   sécurité gagne ; l'escalade est un droit de tout membre de l'équipe.
4. **Honnêteté documentée** : un écart non clôturé reste visible (statut 🔴)
   jusqu'à vérification d'efficacité — aucun « vermifuge documentaire ».
