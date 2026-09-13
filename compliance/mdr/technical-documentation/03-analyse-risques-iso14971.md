# §5 — Gestion des risques (ISO 14971:2019) — MEDISUITE IIb

> Méthode : FMEA process/software (S × O × D, échelle 1-5, indice ≥12 →
> mesure obligatoire). Les risques **projet** R1-R10 de l'audit v0.1 (adhésion
> utilisateurs, chiffrage…) relèvent du plan d'exécution de l'audit, PAS de ce
> dossier : ici, seuls les risques **cliniques patient** dus au dispositif
> sont gérés. Évaluation a posteriori à recalculer après V&V CHU (🔴).

## 1. Contexte d'utilisation et dangers potentiels (ISO 14971 §4)

Utilisateurs : professionnels de santé formés (médecins, radiologues,
biologistes, infirmiers, urgentistes) — **pas de patient utilisateur direct**
(portail patient : consultation de ses propres données). Environnement :
établissements de santé ivoiriens, connectivité intermittente, électricité
instable (UPS/4G assumés dans la conception — dégradation gracieuse).
Séquence de risque principale : erreur IA → décision clinique biaisée →
retard/sur-traitement/sous-traitement.

## 2. FMEA des fonctions cliniques (v0.4)

| ID | Mode de défaillance | Effet patient | S | O | D | Mesures de maîtrise (preuve) | S' O' D' | RPN' |
|---|---|---|---|---|---|---|---|---|
| RM-01 | Faux négatif IA (fusion under-detects) | lésion manquée, retard diagnostic | 5 | 2 | 2 | le clinicien voit importance des modalités + probabilités (explicabilité) ; IFU : outil d'aide, pas de diagnostic autonome ; seuils de confiance affichés | 5 2 1 | 10 |
| RM-02 | Faux positif IA | anxiété, sur-investigations (dose IRM/TDM) | 3 | 3 | 2 | catégorisation BI-RADS avec conduite standardisée ACR ; détection de dérives MLOps | 3 2 2 | 12→mesure : audit périodique 🟠 |
| RM-03 | Biais d'automatisation (automation bias) | le clinicien suit l'IA sans contre-vérification | 5 | 2 | 2 | UI : probabilités non binaires, rappels de contre-indications code AVC, formation obligatoire (IFU) | 5 1 2 | 10 |
| RM-04 | Données d'appariement incorrectes (fusion sur modalités désynchronisées) | inférence sur données non correspondantes au patient | 4 | 2 | 2 | contrôle d'intégrité d'import, identifiants patient liés à chaque modalité, audit chaîné | 4 1 2 | 8 |
| RM-05 | Hors-garantie dérive de modèle (drift) | dégradation silencieuse des prédictions | 4 | 2 | 3 | DAG Airflow data-drift-check ; seuils à calibrer 🔴 ; versionning modèles MLflow | 4 2 2 | 16→ 🟠 calibrage CHU |
| RM-06 | Fuite de données de santé (cyber) | préjudice RGPD/confidentialité, perte de confiance | 5 | 2 | 1 | scrypt, JWT+MFA, RBAC fail-closed, .gitignore durci, chaîne d'audit ; Vault+mTLS+pentest 🔴 | 5 1 1 | 5 |
| RM-07 | Indisponibilité pendant l'urgence (code AVC) | retard de prise en charge critique | 5 | 2 | 2 | dégradation gracieuse (PACS/FHIR hors ligne → soin local continue), HPA 2→6, restart policies ; plan de continuité CHU 🔴 | 5 2 1 | 10 |
| RM-08 | Erreur d'interopérabilité (HL7 FHIR mapping incorrect) | résultat labo attribué au mauvais patient | 5 | 1 | 2 | tests HL7 roundtrip + FHIR validate server-side (HAPI REQUIRE), identifiant OID national, contrôle d'unicité | 5 1 1 | 5 |
| RM-09 | Erreur d'usage UI (mauvaise sélection d'écran/得分) | score calculé sur mauvais contexte clinique | 3 | 3 | 3 | écrans typés TS strict, panel clinique générique avec contexte affiché ; **usabilité IEC 62366 à mener** 🔴 | 3 2 2 | 12→🟠 |
| RM-10 | Couplage excessive aux horloges cliniques (LKW mal saisi) | fenêtre rtPA mal évaluée | 4 | 2 | 2 | horloge LKW explicite + alertes AHA/ASA affichées, validation de cohérence horaire | 4 1 2 | 8 |

## 3. Évaluation globale et acceptabilité (ISO 14971 §7)

- 6/10 risques sous seuil 10 (acceptables en l'état de preuve).
- 4/10 exigent une mesure complémentaire **avant libération clinique** :
  RM-02 (audit périodique des faux positifs), RM-05 (calibrage des seuils de
  drift sur données CHU réelles), RM-09 (validation d'usabilité formelle),
  plus le plan de continuité RM-07.
- **Risque résiduel** : jugé acceptable **conditionnellement** aux mesures
  ci-dessus ET à la formation des utilisateurs — conclusion à entériner par
  le comité de gestion des risques (🔴 à constituer, ISO 13485 §7.3).

## 4. Bénéfice-risque (MDR Annexe I §8, §23.1)

Bénéfice : réduction des délais de priorisation (trauma, AVC), standardisation
des scores cliniques (reproductibilité inter-praticiens), accès à une
expertise imagerie avancée en zone à faible densité de spécialistes — enjeu
de santé publique ivoirien documenté dans la finalité. Risques : faux
négatifs/positifs, dépendance, confidentialité. Le rapport bénéfice/risque
est favorable **sous les mesures de maîtrise ci-dessus** ; cette conclusion
sera revalidée par l'évaluation clinique multicentrique (section 8) avant
dépôt notifié.

## 5. Rôles et livrables

| Livrable ISO 14971 | Propriétaire | État |
|---|---|---|
| Plan de gestion des risques | qualité (à nommer) | 🔴 |
| FMEA maintenue par version | ingénierie + qualité | 🟠 (ce document) |
| Rapport de gestion des risques final | comité des risques | 🔴 |
| Retour PMS → boucle de gestion des risques | 07-pms-vigilance.md | 🔴 |
