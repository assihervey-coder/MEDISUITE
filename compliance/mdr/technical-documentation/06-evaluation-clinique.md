# §8 — Évaluation clinique et investigation clinique (MDR Annexe XIV / XV)

> État : 🔴 **démarrage** — ce document fixe la stratégie. L'évaluation
> clinique multicentrique CHU est le jalon critique de la v1.0.0 ; aucun
> dépôt notifié sans son rapport final.

## 1. Stratégie d'évaluation clinique (Annexe XIV, §1)

MEDISUITE est un logiciel **nouveau** sans dispositif équivalent
commercialisé par le fabricant : la voie « équivalence » seule n'est pas
retenue. La stratégie combine :

1. **Données de littérature** : chaque score clinique embarqué cite son
   référentiel primaire (ESI, qSOFA/SOFA, GCS, Wells, NIHSS, ASPECTS,
   BI-RADS ACR 2013, CURB-65, KDIGO 2021, AJCC 8ᵉ…) — état de l'art
   documenté dans `packages/clinical-rules` (base de l'évaluation de
   conformité aux normes harmonisées).
2. **Performance analytique** : 373+ tests + benchmarks à produire sur banc
   CHU (latence p95 ≤2 s, exactitude par tête de prédiction) — V&V
   `04-iec-62304-classe-C.md`.
3. **Investigation clinique multicentrique** (Annexe XV) : nécessaire pour
   les sorties IA nouvelles (fusion multimodale) — plan ci-dessous.
4. **PMCF** (Annexe XIV Part B) : surveillance continue post-CE via PMS.

## 2. Investigation clinique multicentrique CHU (plan d'étude)

> **Mise à jour v0.6.0** : le protocole détaillé est rédigé —
> `10-protocole-investigation-multicentrique-R5.md` (MEDISUITE-CI-01,
> ISO 14155, 3 CHU, n=600, co-endpoints κ/sûreté/délais, DSMB, ANOC-CI,
> PACTR). Il **supersède l'estimation d'effectifs** ci-dessous (§7.4 du
> protocole justifie l'écart). Les soumissions restent 🔴 (jalon R5).

| Champ | Proposition (à affiner par l'investigateur coordonnateur) |
|---|---|
| Design | étude prospective, multi-centres (2-3 CHU pilotes), cohorte consécutive, comparaison aidé-par-MEDISUITE vs pratique standard historique |
| Endpoints primaires | 1) concordance décision clinique vs gold standard adjudiqué ; 2) délai priorisation (triage → orientation) ; 3) pour le module code AVC : respect des fenêtres rtPA/thrombectomie |
| Endpoints secondaires | précision (AUC, sensibilité, spécificité) par tâche IA, taux d'erreur d'usage, charge de travail (NASA-TLX), satisfaction |
| Populations | patients adultes admis aux urgences/imagerie/laboratoire des centres participants ; exclusions : mineurs (hors pédiatrie dédiée), urgences vitales immédiates non éthiques |
| Taille | calculée par endpoint (ordre de grandeur : 300-500 patients par site — à justifier statistiquement) |
| Sécurité | comité scientifique + comité d'éthique CHU, conformité bonnes pratiques (ISO 14155 si investigation) |
| Données | pseudonymisation systématique, hébergement local, registre d'audit chaîné, DPIA par site |
| Durée | M+0 accord CHU → M+6 inclusion → M+12 analyse → M+15 rapport final |

## 3. Libération des modèles IA (qualification par configuration)

Chaque modèle entraîné (FusionEngine torch, ADR 0022-0023) est une
**configuration du dispositif** avec son propre dossier : jeu de données
(déclaré, DVC), métriques de performance analytique, analyse de biais
(populations ivoiriennes représentées), explication (importance modalités,
attention), version MLflow, et signature de libération par le comité. Le
pipeline MLOps (MLflow, DVC, Airflow retrain+drift) applique ce processus à
chaque itération — les seuils de drift restent à calibrer sur données CHU
réelles (RM-05).

## 4. Évaluation des données cliniques — lignes directrices MEDDEV 2.7/1 rev 4

Plan de rapport : identification du dispositif, état de l'art (par
spécialité embarquée), démonstration de conformité aux EGSP via preuves
analytiques + littérature + investigation, analyse bénéfice-risque revalidée,
conclusions sur la conformité. Le rapport sera rédigé par un évaluateur
clinique **indépendant** du développeur (exigence MDR §61.10 pour les
logiciels de classe IIb sans prédicat).

## 5. Chronologie vers le rapport final d'évaluation clinique

1. 🔴 Protocole d'investigation finalisé + accords CHU + comité d'éthique.
2. 🔴 Banc de performance analytique (matériel cible K8s GPU, jeux de test).
3. 🔴 Exécution + monitoring (DSMB trimestriel).
4. 🔴 Rapport final + mise à jour du bénéfice-risque + IFU définitive.
5. 🟢 Plan PMCF/PMS déjà structuré → `07-pms-vigilance.md`.

## 6. Limites déclarées (honnêteté d'ingénieur)

- Les **données d'appariement multimodales réelles** sont rares dans le
  contexte ivoirien (constat d'audit v0.1) : l'investigation CHU doit
  constituer ce corpus — c'est aussi sa valeur scientifique.
- Les scores cliniques embarqués sont des **implémentations de référentiels
  publiés** : leur évaluation porte sur la conformité d'implémentation (tests)
  et l'usage, pas sur la validité clinique des référentiels eux-mêmes.
- Aucune claim de supériorité sur la pratique standard tant que l'étude
  multicentrique n'est pas conclue.
