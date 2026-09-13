# Protocole d'évaluation sommative de l'usage (IEC 62366-1 §5.8-5.9)

> Statut : protocole rédigé, exécution 🔴 R6 (jalon usabilité, plan
> `08-plan-validation-v1.0.0.md`). Condition de libération v1.0.0.
> Précédé par l'évaluation formative (`protocole-evaluation-formative.md`,
> R3) dont les corrections UI seront re-vérifiées ici.
> Données synthétiques uniquement (seed ivoirien) — aucun patient réel.
> L'évaluation ne peut être sommative qu'après CONGELATION de l'interface
> (plus aucune itération d'UI prévue) — règlement IEC 62366-1 §5.8.1.

## 1. Objectif

Démontrer, sur l'interface congelée, que les **risques d'usage** identifiés
par la FMEA (`03-analyse-risques-iso14971.md` : RM-03 biais
d'automatisation, RM-09 erreur d'usage UI, RM-10 horloge LKW, RM-01/RM-02
sorties IA) sont réduits à un niveau acceptable dans les conditions réelles
d'usage. La sortie conditionne : clôture de RM-09, mise à jour des IFU,
libération v1.0.0 (PROC-07), et alimente le CER TD-11 (MEDDEV 2.7/1 §5.4 —
ergonomie comme preuve de bénéfice-risque).

## 2. Scénarios d'usage reliés aux dangers (use-related risk analysis)

Chaque scénario teste explicitement une chaîne « usage → danger » :

| Scénario (écran) | Chaîne usage → danger testée | Risque FMEA |
|---|---|---|
| S1 — TriageBoard (ESI) | mauvaise catégorisation → retard de prise en charge vitale | RM-09 |
| S2 — StrokeCode | LKW mal saisi → fenêtre rtPA mal évaluée → hémorragie/inefficacité | RM-10 |
| S3 — BiRadsViewer | confusion catégorie/conduite → sous- ou sur-investigation | RM-02, RM-09 |
| S4 — Laboratoire (workflow) | résultat critique non traité → préjudice patient | RM-08, RM-09 |
| S5 — FusionViewer (modalité manquante) | confiance IA mal interprétée → diagnostic fondé sur données incomplètes | RM-01, RM-03 |
| S6 — ECRF (saisie + signature) | saisie erronée signée → données d'investigation biaisées | RM-04, RM-09 |
| T7 — Recherche patient + AuditLog | mauvais patient sélectionné → acte/fiche attribuée au mauvais patient | RM-04, RM-09 |
| S8 — StudyStatus/Lock (promoteur)* | verrou posé sans préconditions → base gelée à tort | RM-09 |

\* S8 : 2 participants promoteur (hors comptage des 15 cliniciens) —
utilisateurs distincts des groupes cliniques, parcours à conséquence
d'investigation.

## 3. Participants

| Paramètre | Exigence |
|---|---|
| Effectif | **≥ 15** cliniciens utilisateurs réels (+ 2 promoteurs pour S8) |
| Répartition | ≥ 5 par groupe d'usage : urgence (S1/S2), imagerie (S3/S5), laboratoire (S4) ; tous passent S6/T7 |
| Prérequis | formation initiale PROC-06 validée (usage post-formation, pas intuitivité à froid) ; expérience d'au moins 6 mois dans le domaine |
| Exclusions | toute personne ayant contribué au développement/conception (déviation interdite), étudiants non autorisés à pratiquer seul |
| Recrutement | investigateurs CHU de CI-01 (COC/TRI/YOP/BOU) — registre investigateurs ; consentement écrit (anonymat code P-xx) |

## 4. Décor et conditions

- CHU pilote, salle calme, **matériel réel** (laptop + écran, like CHU) ;
- données synthétiques seed ivoirien (manifest datasets) — aucun patient réel ;
- réseau normal PUIS dégradé simulé (mode offline du portal) sur S6 ;
- interface **congelée** (tag Git consigné au rapport) ; configuration
  plateforme = variante Complete (38 services) ;
- enregistrement écran avec accord écrit ; chronométrage discret.

## 5. Tâches et critères de succès (mesures prédéfinies)

| # | Tâche donnée au participant | Mesures | Critère de succès (N=15) |
|---|---|---|---|
| S1 | « Priorisez ces 6 patients et justifiez 2 catégorisations » | succès, temps, erreurs de catégorie | 100 % sans erreur de priorité vitale ; ≥ 90 % succès |
| S2 | « Patient LKW=2h30, NIHSS à compléter : établissez l'éligibilité rtPA » | exactitude LKW, fenêtres affichées, lecture contre-indications | 100 % fenêtres correctes ; 0 omission de contre-indication critique |
| S3 | « Catégorisez ces 3 mammographies et donnez la conduite » | catégorie vs gold standard, conduite citée | ≥ 90 % ; 0 confusion catégorie/conduite |
| S4 | « Validez ou rejetez ces 4 résultats dont 1 critique » | action sur le résultat critique | 100 % sur le résultat critique |
| S5 | « Interprétez la synthèse multimodale avec 1 modalité manquante » | compréhension de la confiance recalibrée (question ouverte) | reformulation correcte ≥ 90 % (≥ 14/15) |
| S6 | « Saisissez ce formulaire eCRF, signez-le, puis passez en mode dégradé et resynchronisez » | complétude, signature, idempotence perçue après resync | 0 perte de saisie ; 100 % signature sans ambiguïté |
| T7 | « Retrouvez ce patient, puis vérifiez qui a accédé à son dossier » | recherche correcte, lecture de la chaîne d'audit | ≥ 90 % ; 0 sélection de mauvais patient |
| S8 | « Posez le verrou M+18 en respectant les préconditions » | lecture préconditions, 2 témoins, confirmation typée | 0 verrou sans préconditions (tâche pensée pour échouer proprement si préconditions non lues) |

Critères GLOBAUX de réussite du test sommatif :

1. **0 erreur d'usage dangereuse non détectée** (l'erreur existe éventuellement
   mais est détectée/récupérée par l'interface ou le participant) ;
2. **≥ 90 % de succès par tâche critique** (S1-S6) sur l'ensemble des 15 ;
3. aucune séquence d'usage créant un **risque résiduel inacceptable** non
   traité par la FMEA.

## 6. Méthode de passation

1. **Sans assistance pendant la tâche** : le modérateur n'intervient pas
   (différence clé avec le formatif) ; sondes posées UNIQUEMENT après
   échec ou à la fin du scénario (« qu'est-ce qui vous a guidé ? »).
2. Script de consignes standardisé (lire mot à mot) ; ordre des scénarios
   alterné entre participants (contre-balancement) pour neutraliser
   l'effet d'apprentissage.
3. Enregistrement : `grille-sommative.md` par participant + capture écran.
4. Fin de session : NASA-TLX + question automation bias (« dans quelle
   mesure suivriez-vous la suggestion IA sans contre-vérifier ? ») —
   échec global si moyenne > 3/5 → mesure de conception requise.
5. Toute déviation au protocole est consignée (registre déviations
   `compliance/mdr/clinical/monitoring/registre-deviations.md`) et
   justifiée au rapport.

## 7. Analyse et classification des erreurs

- Taxonomie : erreur **potentiellement dangereuse** (effet patient) /
  **opérationnelle** (retard, reprise) ; détection : par l'interface /
  par le participant / non détectée ;
- Analyse par sous-groupe (urgence vs imagerie vs laboratoire) ;
- Rapprochement FMEA : chaque erreur observée est mappée à un RM et
  ré-évaluée (sévérité × occurrence × détection) ;
- Décision : si un critère de §5 échoue → mesure de conception + re-test
  de la tâche concernée sur N ≥ 15 nouveaux participants (interface
  re-congelée, nouvelle itération sommative complète).

## 8. Rapport sommatif (livrable IEC 62366-1, annexe TD-07)

Modèle : `modele-rapport-sommative.md`. Le rapport est annexé au dossier
technique (§7 Ingénierie d'usage, `05-iec-62366-usabilite.md`), référencé
au CER TD-11 et aux IFU (mises à jour des conduites par écran si requise).

## 9. Éthique

Consentement écrit (participation + enregistrement), anonymisation par
codes P-xx, aucune donnée patient réelle, droit de retrait sans justification,
archivage 10 ans (PROC-01). Conformité loi ivoirienne 2013-450 (données à
caractère personnel) — DPIA déjà cartographiée dans les soumissions.

## 10. Liens

- Formative : `protocole-evaluation-formative.md` + `grille-passation.md` (R3) ;
- FMEA : `03-analyse-risques-iso14971.md` (RM-01, RM-02, RM-03, RM-04, RM-08, RM-09, RM-10) ;
- EGSP Annexe I §14.2 (interfaces ergonomiques) ; §5.8 IEC 62366-1:2015+A1:2020 ;
- IFU : `ifu/` — alignées sur les résultats sommatifs ;
- Plan de validation : `08-plan-validation-v1.0.0.md` (jalon usabilité R6) ;
- CER : `11-rapport-evaluation-clinique-meddev-271.md` (TD-11 §5.4).
