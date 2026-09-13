# PROC-04 — Incidents, non-conformités et actions correctives/préventives (CAPA)

**Propriétaire** : RQ | **Revue** : mensuelle | **Version** : 1.0

## 1. Finalité

Capturer toute défaillance (bug clinique, incident de sécurité, near-miss,
réclamation) et la transformer en **action vérifiée pour efficacité** —
la boucle CAPA est l'artère du SMQ et alimente la vigilance (MDR art. 87).

## 2. Registre des incidents (à créer, espace CHU)

Champs obligatoires : ID (INC-AAAA-NNN), date/détection/escalade, service
et module concernés, sévérité (S1 décès possible → S5 cosmétique),
description factuelle, données probantes (spans OTel, entrées de chaîne
d'audit, captures), classification vigilance (rapportable oui/non + échéance),
décision, propriétaire, date de clôture.

## 3. Flux de traitement

1. **Détection** (support CHU, alerte Prometheus/OTel, revue d'audit chaîné,
   drift MLOps, utilisateur) → ouverture ≤ 1 jour ouvré.
2. **Triage ≤ 48 h** : sévérité ; S1/S2 → escalation immédiate direction +
   revue vigilance (rapport autorité ≤ 2/10 jours selon art. 87) + décision
   de containment (feature flag, rollback GitOps).
3. **Analyse de cause** (5 pourquoi / Ishikawa) → mise à jour FMEA (PROC-02).
4. **Action corrective** (fix + test régressif obligatoire dans la même PR)
   et/ou **préventive** (amélioration procédure/IFU/formation).
5. **Vérification d'efficacité** à 30-90 jours (critère mesurable annoncé
   d'avance) — sans elle, la fiche reste ouverte.
6. **Clôture** par le RQ, liée au PV de revue mensuelle.

## 4. Interface avec le dépôt

- Tout bug fix corrigeant un incident porte la référence `INC-…` dans le
  message de commit (traçabilité code ↔ qualité).
- Les incidents S1/S2 déclenchent une note utilisateurs (PROC-07 §6) et
  l'examen de la nécessité d'une notice de sécurité.

## 5. Indicateurs

- Délai moyen détection→triage (cible ≤ 2 j) ; délai S1/S2→containment
  (cible ≤ 24 h) ; taux de récidive post-CAPA (cible 0) ; nb de fiches
  ouvertes > 90 jours (cible ≤ 3).
