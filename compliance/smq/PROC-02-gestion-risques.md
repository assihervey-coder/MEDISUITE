# PROC-02 — Gestion des risques (ISO 14971:2019, transversal SMQ)

**Propriétaire** : Responsable qualité + ingénierie | **Revue** : à chaque release + annuelle | **Version** : 1.0

## 1. Finalité

Assurer que les risques liés à MEDISUITE sont identifiés, évalués, maîtrisés
et **re-évalués en continu** du développement à l'après-commercialisation,
avec une boucle PMS → FMEA explicite (MDR Annexe I §3).

## 2. Plan de gestion des risques

Contenu obligatoire (maintenu dans le dossier CE) :
1. Périmètre : risques **cliniques patient** du dispositif (les risques
   projet relèvent du plan d'exécution de l'audit — frontière documentée
   dans `03-analyse-risques-iso14971.md` §1).
2. Critères d'acceptabilité : échelle S/O/D 1-5, RPN = S×O×D, seuil 12 ;
   tout risque ≥ 12 exige une mesure de maîtrise avec vérification.
3. FMEA maintenue : `03-analyse-risques-iso14971.md` (IDs RM-01…RM-10).
4. Bénéfice-risque global : revalidé à chaque release et par l'évaluation
   clinique (jalon R7).

## 3. Déclencheurs de mise à jour FMEA

| Événement | Action | Délai |
|---|---|---|
| Release logicielle | revue des RM-* concernés par le CHANGELOG | avant tag |
| Incident CAPA (PROC-04) | nouveau RM-* ou réévaluation | ≤ 10 jours |
| Changement de modèle IA (libération de modèle) | revue dérive/biais (RM-05) | avant déploiement |
| Retour PMS / usabilité | réévaluation O et D | ≤ 15 jours |
| Veille normative (ACR, AHA/ASA, KDIGO…) | impact sur référentiels embarqués | semestrielle |

## 4. Vérification des mesures de maîtrise

Chaque mesure cite sa preuve (test automatisé, écran, procédure, IFU) ;
une mesure non vérifiable est un écart ouvert. Exemple : RM-06 (fuite de
données) → scrypt/JWT/MFA/RBAC prouvés par tests, pentest à venir (jalon
R4, plan `security/hardening/pentest/`).

## 5. Enregistrements & indicateurs

- Enregistrements : FMEA versionnée par release (dans le dossier CE),
  fiches de réévaluation, rapports bénéfice-risque.
- Indicateurs : nb de risques ≥ 12 non clôturés (cible : 0 à la libération
  clinique) ; âge moyen des mesures ouvertes (cible ≤ 60 jours).
