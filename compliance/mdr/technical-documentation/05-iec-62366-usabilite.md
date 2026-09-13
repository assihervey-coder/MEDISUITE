# §7 — Ingénierie d'usage (IEC 62366-1:2015+A1) — plan de validation d'usage

> État : 🔴 **à mener** — ce document fixe le plan. Aucune utilisation
> clinique n'est autorisée avant exécution du summative usability testing
> (§5) et clôture des risques d'usage RM-02/RM-03/RM-09.

## 1. Spécification d'usage (Use Specification)

| Élément | Spécification |
|---|---|
| Utilisateurs professionnels | médecins, radiologues, biologistes, infirmiers, urgentistes, administrateurs, auditeurs (10 rôles RBAC) |
| Environnement d'usage | salle de garde, cabinet de radiologie, laboratoire, lit du patient ; éclairage variable, interruptions fréquentes (urgences), réseaux intermittents |
| Patient population | patients des établissements de santé ivoiriens, tous âges (selon module) |
| Partie du corps interagissant | n/a (logiciel) — interaction clavier/souris/tactile |
| Focus d'attention | écrans de priorisation (TriageBoard ESI), code AVC (horloge LKW + NIHSS + ASPECTS), BI-RADS viewer |

## 2. Caractéristiques liées à l'usage et scénarios critiques

Fonctions à risque d'usage identifié (croisées avec la FMEA) :
1. **Saisie de l'heure de dernière connaissance vue (LKW)** — code AVC :
   une erreur de saisie change la fenêtre rtPA/thrombectomie (RM-10).
2. **Lecture des probabilités de malignité BI-RADS** — l'utilisateur doit
   distinguer catégorie ACR (0-6) et probabilité (%) (RM-02, RM-03).
3. **Priorisation trauma (ISS, triage)** — erreur de triage → retard de prise
   en charge.
4. **Validation de résultats critiques** (laboratoire) — clic erroné sur
   validation par rapport à rejet.
5. **FusionViewer** — l'utilisateur doit comprendre que l'importance des
   modalités est une aide, pas un diagnostic (RM-03).

## 3. Interface utilisateur — analyse analytique (formative, déjà possible)

Éléments de conception existants qui réduisent le risque d'usage :
- écrans typés TypeScript strict (contrat de données) et i18n fr/en ;
- fenêtres thérapeutiques **affichées** (pas cachées) avec couleurs codées
  et contre-indications explicites sur l'écran code AVC ;
- échelle BI-RADS colorée 0-6 avec conduite recommandée ACR par catégorie ;
- panel clinique générique : le contexte (patient, module, score) est
  toujours affiché en tête d'écran ;
- tous les changements d'état produisent un événement d'audit (piste).

## 4. Évaluation formative (prévue, itérations 2-3)

- **Walkthrough cognitif** avec 5 praticiens pilotes sur les 5 scénarios
  critiques ci-dessus ; tâches : « prioriser ce tableau de triage », «
  établir l'éligibilité rtPA d'un patient LKW=2h30 NIHSS=14 », « catégoriser
  cette mammographie BI-RADS 4 »…
- Mesures : taux de succès par tâche, erreurs de saisie LKW, temps de
  recherche d'une information critique, heuristiques de Nielsen complément.
- Sortie : rapport d'évaluation formative + corrections UI (itération).

## 5. Summative usability testing (condition de libération)

> **Protocole complet rédigé (v0.11)** : `usability/protocole-evaluation-sommative.md`
> (8 scénarios reliés aux dangers, N≥15+2 promoteurs, critères globaux,
> contre-balancement) + grille par participant `usability/grille-sommative.md`
> + modèle de rapport normatif `usability/modele-rapport-sommative.md`.
> Exécution 🔴 R6 sur interface congelée.

| Paramètre | Cible |
|---|---|
| Participants | ≥15 utilisateurs professionnels répartis sur les 3 groupes d'usage (urgence, imagerie, laboratoire) |
| Décor | environnement simulé proche réel (CHU pilote, données synthétiques seed ivoirien) |
| Tâches | les 5 scénarios critiques + 2 tâches d'entretien (recherche patient, vérification audit) |
| Critère de succès | 0 erreur d'usage à conséquence clinique potentiellement dangereuse non détectée ; ≥90 % de succès par tâche critique |
| Sortie | rapport sommatif IEC 62366 annexé au dossier, clôture RM-09 et mise à jour IFU |

## 6. Liens

- FMEA : `03-analyse-risques-iso14971.md` (RM-02, RM-03, RM-09, RM-10).
- EGSP 14.2 (interfaces ergonomiques, réduction des risques d'usage).
- IFU : les manuels d'utilisation seront alignés sur les résultats sommatifs
  (conduite à tenir par écran, limites d'usage, formation requise).
