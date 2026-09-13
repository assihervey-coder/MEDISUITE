# Notice d'utilisation (IFU) — Profil CLINICIEN

> MEDISUITE v0.5 — document à valider par l'évaluation d'usabilité sommative
> (IEC 62366) avant libération clinique. Support : support@medisuite.ci (canal
> CHU : notification-service). **Formation initiale obligatoire (PROC-06)
> avant compte actif.**

## 1. Ce que MEDISUITE est — et n'est pas

MEDISUITE est une **aide à la décision clinique** : priorisation des
patients (triage ESI), scores cliniques validés par référentiels (qSOFA,
GCS, NIHSS, Wells…), imagerie DICOM/OHIF, résultats de laboratoire avec
alertes critiques, synthèse multimodale par IA. **MEDISUITE ne remplace pas
votre jugement** : aucune décision thérapeutique ne doit reposer uniquement
sur ses sorties ; la responsabilité médicale reste entière (finalité
MDR — `intended-purpose.md`).

## 2. Avertissements critiques (à lire en premier)

1. **Code AVC** : l'horloge LKW saisie commande les fenêtres rtPA/thrombectomie
   affichées — vérifiez systématiquement l'heure affichée à l'écran contre
   la source clinique (témoin, dernier vu bien) avant toute décision.
2. **BI-RADS** : la catégorie ACR (0-6) et la probabilité de malignité
   affichées sont une aide de catégorisation ; la conduite recommandée suit
   l'ACR 2013 mais ne remplace pas le compte rendu radiologique signé.
3. **Alertes critiques labo** : une valeur critique notifiée exige une
   acquittalité documentée (traçée dans la chaîne d'audit).
4. **FusionViewer (IA)** : l'importance des modalités est explicative
   (pourquoi le modèle penche vers une hypothèse), jamais une preuve
   diagnostique. Confiance recalibrée affichée quand des modalités manquent.
5. **Panne/indisponibilité** : le soin continue sans MEDISUITE (dégradation
   gracieuse) ; ne retardez jamais un geste urgent pour attendre le système.

## 3. Mode d'emploi par tâche (référence aux écrans)

| Tâche | Écran | Points de vigilance |
|---|---|---|
| Prioriser le tableau d'attente | TriageBoard (ESI) | catégorisation 1-5, réévaluer à chaque ré-admission |
| Calculer un score | ClinicalPanel du module | le score cite son référentiel ; saisir les paramètres complets |
| Déclarer un code AVC | StrokeCode | LKW → NIHSS (13 items) → ASPECTS → contre-indications → synthèse |
| Catégoriser une mammographie | BiRadsViewer | catégorie 0-6 + densité A-D + conduite ACR |
| Lire l'imagerie | Imagerie → bouton « OHIF ↗ » | ouverture de la série via le PACS |
| Consulter la synthèse multimodale | FusionViewer | vérifier les modalités importées et la confiance |
| Suivre une valeur critique | Labo (workflow) | notification bicanale + acquittalité |
| Vérifier la traçabilité | AuditLog (auditeurs) | chaîne SHA-256 vérifiable |

## 4. Erreurs fréquentes et récupération

- « 403 permission requise » : votre rôle n'a pas la permission demandée —
  adressez-vous à l'administrateur (matrice RBAC).
- « serveur FHIR/PACS injoignable » : les fonctions locales restent
  disponibles ; le relais central réessaiera automatiquement.
- Saisie erronée validée : contactez l'administrateur — toute correction est
  tracée (jamais effacée), l'audit conserve l'historique.

## 5. Formation et recyclage

Formation initiale 2 h + quiz ≥ 80 % (PROC-06), validation pratique des 3
scénarios critiques (AVC, BI-RADS, triage) sur données synthétiques,
recyclage annuel et à chaque release majeure (note de version).
