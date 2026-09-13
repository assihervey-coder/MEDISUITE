# §9 — Surveillance après commercialisation (PMS) et vigilance (MDR art. 83-90)

> État : 🔴 **plan** — les mécanismes techniques existent (v0.1-v0.4), les
> procédures qualité et les rapports PMS-PMCF sont à instaurer avant v1.0.0.

## 1. Plan de surveillance après commercialisation (PSUR, art. 86)

| Source de données | Mécanisme MEDISUITE | Fréquence de revue |
|---|---|---|
| Incidents et almost-incidents | registre d'incidents qualité (à créer 🔴) + issues Git étiquetées `incident` | continue ; revue mensuelle |
| Signalements utilisateurs | canal support CHU + formulaire intégré (notification-service) | continue |
| Dérive des modèles IA | DAG Airflow `data-drift-check` + MLflow tracking ; seuils RM-05 à calibrer CHU | hebdomadaire automatisée |
| Télémétrie | spans OTel (latence p95, taux d'erreur 5xx par service, Prometheus job `otel`) | tableau de bord Grafana, revue mensuelle |
| Chaîne d'audit | vérification d'intégrité `audit_chain.verify()` (accès, exports, consentements) | mensuelle |
| Réclamations / satisfaction | enquête annuelle praticiens pilotes | annuelle |
| Littérature & veille normative | revue des référentiels cliniques cités (ACR, AHA/ASA, KDIGO…) | semestrielle |

Rapport : **PSUR classe IIb** = mise à jour annuelle (art. 86) — modèle de
rapport 🔴, propriétaire : comité qualité.

## 2. Plan PMCF (Annexe XIV Part B)

Méthodes retenues : études PMCF (prolongation de l'investigation multicen-
trique en phase PMCF), analyse des données réelles d'usage (KPIs analytics),
retours d'expérience formulaires, veille scientifique. Objectifs :
revalider le bénéfice-risque en usage réel, détecter les effets inattendus,
surveiller l'appropriation (formation continue nécessaire ?).

## 3. Vigilance (art. 87-90) — procédure prévue

1. **Incident grave** (décès, détérioration grave, ou almost-incident
   rapportable) : signalement fabricant → autorité compétente.
   - Horizon UE : rapport initial ≤10 jours (2 jours si décès/altération
     imprévue grave), rapport final ≤30/60 jours selon type.
   - Contexte Côte d'Ivoire : accord de reconnaissance mutuelle avec
     l'autorité nationale (pharmaco-vigilance/dispositifs) 🔴 à construire.
2. **Traçabilité interne** : chaque incident est un enregistrement de la
   chaîne d'audit (immuable), un ticket étiqueté, et une action FMEA
   (mise à jour `03-analyse-risques-iso14971.md`).
3. **Actions de terrain** : notice de sécurité, correctif logiciel (release
   d'urgence via GitOps ArgoCD), retrait de fonctionnalité (feature flag),
   jusqu'au rappel de version — procédure détaillée 🔴.

## 4. Boucle PMS → conception (boucle de qualité)

```
usage réel (OTel + audit + incidents)
        │
        ▼
PSUR/PMCF (revue qualité mensuelle/annuelle)
        │
        ├── action FMEA (mise à jour risques + mesures)
        ├── exigence EGSP nouvelle (02-gspr)
        ├── demande de modification (MDR art. 2(109) : substantialité)
        └── itération logicielle (release + CHANGELOG + note utilisateurs)
```

Toute modification substantielle re déclenche la revue du dossier technique
(00-index, §« Processus de revue »).

## 5. Infrastructure PMS déjà en place (preuves v0.4)

- Télémétrie OTel sur les 38 services (v0.4) — base des indicateurs.
- Chaîne d'audit IEC 81001-5-1 avec vérification d'altération.
- Alertes Prometheus cliniques/IA + notification bicanale (SMS/email).
- Analytics KPIs cross-base + épidémiologie (PNLP, 90-90-90).
- Versioning modèles MLflow/DVC pour la surveillance de dérive.

Les procédures documentaires (registre incidents, PSUR template, procédure
vigilance, plan PMCF) sont les livrables ISO 13485 associés — tracés dans
`09-smq-iso13485.md` et le plan `08-plan-validation-v1.0.0.md`.
