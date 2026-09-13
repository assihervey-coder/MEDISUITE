# Protocole d'évaluation formative de l'usage (IEC 62366-1 §5.5-5.8)

> Statut : protocole prêt à passer (participants CHU pilotes) — jalon R3.
> Précède le test sommatif (`05-iec-62366-usabilite.md` §5). Données
> synthétiques uniquement (seed ivoirien) — aucun patient réel.

## 1. Objectif

Identifier les **risques d'usage** des 5 scénarios critiques et vérifier
l'efficacité des mesures de conception (formative = améliorante, 2-3
itérations attendues) avant l'investigation clinique. Lieu : CHU pilote,
salle calme, matériel réel (laptop + écran), réseau normal et simulé
dégradé.

## 2. Participants

5 professionnels par itération, profils croisés : 1 urgentiste, 1 médecin
généraliste, 1 radiologue, 1 biologiste, 1 infirmier — formés selon PROC-06
(formation initiale passée, pour mesurer l'usage réel post-formation, pas
l'intuitivité à froid).

## 3. Scénarios et tâches (mesures prédéfinies)

| # | Scénario (écran) | Tâche donnée | Mesures | Critère |
|---|---|---|---|---|
| S1 | TriageBoard (ESI) | « Priorisez ces 6 patients et justifiez 2 catégorisations » | succès, temps, erreurs de catégorie | 100 % sans erreur de priorité vitale |
| S2 | StrokeCode | « Patient LKW=2h30, NIHSS à compléter : établissez l'éligibilité rtPA » | exactitude LKW saisie, cohérence fenêtres affichées, lecture contre-indications | 100 % des fenêtres correctes ; 0 omission de contre-indication critique |
| S3 | BiRadsViewer | « Catégorisez ces 3 mammographies et donnez la conduite » | catégorie ACR correcte vs gold standard, conduite citée | ≥ 90 % ; 0 confusion catégorie/conduite |
| S4 | Labo (workflow) | « Validez ou rejetez ces 4 résultats dont 1 critique » | action correcte sur le critique (acquittalité) | 100 % sur le résultat critique |
| S5 | FusionViewer | « Interprétez la synthèse multimodale avec 1 modalité manquante » | compréhension de la confiance recalibrée (question ouverte) | reformulation correcte ≥ 4/5 participants |

Scénario d'entretien (sans mesure de temps) : retrouver la traçabilité d'un
accès patient (AuditLog) et vérifier la chaîne.

## 4. Méthode de passation

1. Walkthrough cognitif : penser à voix haute, facilitateur neutre
   (interventions scriptées uniquement).
2. Enregistrement : grille par participant (`grille-passation.md`) + écran
   (avec accord écrit) ; chronométrage discret.
3. Après chaque scénario : 2 questions (difficulté perçue 1-5 ; « qu'est-ce
   qui aurait pu vous tromper ? »).
4. Fin : NASA-TLX global + question automation bias (« dans quelle mesure
   suivriez-vous la suggestion IA sans contre-vérifier ? » — signal d'alerte
   si moyenne > 3/5).

## 5. Analyse et sortie

1. Consolidation des grilles ; classification des difficultés : S « de
   sécurité » (effet patient possible) / O « opérationnel ».
2. Risque d'usage nouveau ou réévalué → FMEA (RM-02, RM-03, RM-09, RM-10).
3. Actions UI (corrections écrans) ou IFU (renforcement) tracées en
   issues ; itération suivante jusqu'à critères ≥ cibles.
4. **Sortie** : rapport d'évaluation formative (modèle de la grille
   consolidée) annexé au dossier CE §7 ; passage au sommatif autorisé quand
   aucun risque d'usage de sécurité n'est ouvert.

## 6. Éthique et données

Aucune donnée patient réelle ; accord de participation écrit ; enregistrements
détruits après consolidation (90 jours) ; résultats anonymisés.
