# PROC-07 — Libération d'une version (release) (ISO 13485 §7.5.9 / MDR art. 13.2)

**Propriétaire** : Ingénierie + RQ | **Revue** : à chaque release | **Version** : 1.0

## 1. Finalité

Formaliser la décision « cette version est libérable » — la libération est
un acte qualité, pas un simple `git tag`. Cette procédure codifie ce que
v0.1→v0.4 faisaient de façon informelle (CHANGELOG + tags + tests).

## 2. Checklist de libération (bloquante)

- [ ] CI verte : 4 niveaux de tests (packages, IA, 38 services, UI tsc/build).
- [ ] Revue des risques concernés (PROC-02) : aucun RM-* ≥ 12 sans mesure close.
- [ ] Migrations de schéma testées sur copie de base ; script de rollback prêt.
- [ ] CHANGELOG rédigé (Keep a Changelog) ; note utilisateurs prête (delta + actions attendues).
- [ ] Images/version épinglées ; SBOM régénéré (jalon R4) ; scan CVE sans critique ouverte.
- [ ] Télémétrie active (OTel/Prometheus) vérifiée sur l'environnement de staging.
- [ ] FMEA versionnée ; dossier CE mis à jour si modification substantielle (MDR art. 2(109)).
- [ ] Approbation signée (développeur + RQ ; direction si S1/S2 en attente).

## 3. Modalités techniques (déjà opérationnelles)

1. Tag Git annoté (`v0.x.0`) + push `main --tags`.
2. GitOps (ArgoCD/Flux) : propagation contrôlée par environnement
   (dev → staging → site pilote), rollback = revert tag.
3. Notes de version : CHANGELOG + canal support CHU (notification-service).

## 4. Après libération

- Surveillance renforcée 72 h (tableau Grafana + alertes) — seuils OTel.
- Toute anomalie post-libération → PROC-04 (incidents/CAPA).

## 5. Enregistrements

Checklist signée (archive qualité), note utilisateurs, PV de surveillance
72 h. Indicateur : nb de releases avec rollback < 72 h (cible 0), délai de
propagation dev→pilote.
