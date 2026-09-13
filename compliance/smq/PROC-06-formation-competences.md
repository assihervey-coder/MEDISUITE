# PROC-06 — Formation et compétences (ISO 13485 §6.2)

**Propriétaire** : Direction + RQ | **Revue** : semestrielle | **Version** : 1.0

## 1. Finalité

Garantir que chaque personne agissant sur le dispositif (équipe fabricant)
ou avec lui (utilisateurs CHU) possède les compétences exigées — la
formation est aussi une **mesure de maîtrise des risques** (RM-03 automation
bias : IFU + formation obligatoire).

## 2. Équipe fabricant (matrice de compétences)

| Rôle | Exigences minimales | Habilitation |
|---|---|---|
| Développeur | conventions repo (référentiels cités dans les docstrings de scores), revue par les pairs, tests | fiche habilitation signée après 1ère PR majeure |
| Ingénieur IA | comprendre ADR 0022/0023, limites des modèles, DVC/MLflow | idem |
| RQ | ISO 13485/14971/62304 de base, dossier CE | formation externe certifiante (🔴 à planifier) |
| Responsable réglementaire | MDR, EUDAMED, vigilance | idem 🔴 |

## 3. Utilisateurs CHU (liée à l'IFU et à l'usabilité)

1. **Formation initiale obligatoire** avant compte actif : 2 h (cliniciens),
   4 h (administrateurs/techniciens) — programme tiré de l'IFU, quiz ≥ 80 %.
2. **Scénarios critiques** (code AVC LKW, BI-RADS, triage ESI) : validation
   pratique sur données synthétiques — alignée sur le protocole usabilité.
3. **Recyclage** : annuel + à chaque release majeure (note de version + delta).

## 4. Enregistrements & indicateurs

- Fiches individuelles de formation (date, contenu, formateur, évaluation),
  registre collectif par site.
- Indicateurs : 100 % des comptes actifs = formation à jour (contrôlable
  via attribut utilisateur) ; taux de réussite quiz ; recyclages dans les
  temps (cible ≥ 95 %).
