# Registre des déviations de protocole — MEDISUITE-CI-01

> **Objet** : registre central des déviations (ISO 14155 §5.6 / EGSP).
> Ouvre une ligne dès qu'une déviation est constatée (monitoring, site,
> data manager — contrôle de cohérence) ou par l'eCRF lui-même (rejet 422
> récurrent, panne site 24 h). Revu à **chaque réunion DSMB** ; toute
> déviation majeure déclenche : notification promoteur ≤ 24 h, évaluation
> d'impact bénéfice-risque (mise à jour RM-01…RM-10 si nouveau risque),
> et information ANOC-CI si elle affecte les droits/sécurité des participants.

| DEV-NNN | Date | Site | Sujet (code) | Description | Majeure ? | Cause racine | Action corrective (CAL) | Responsable | Échéance | Clôturée | Rapport de visite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV-001 | ⟦…⟧ | ⟦CHU-…⟧ | CI01-⟦…⟧ | ⟦ex. inclusion hors critère détectée à SDV⟧ | ⟦oui/non⟧ | ⟦…⟧ | ⟦…⟧ | ⟦…⟧ | ⟦date⟧ | ⟦date⟧ | MV-⟦2026⟧-⟦NNN⟧ |
| DEV-002 | | | | | | | | | | | |
| DEV-003 | | | | | | | | | | | |

**Typologie à coder dans la description** (statistique des causes) :
`E-ELIG` (éligibilité), `E-CONS` (consentement/ré-information),
`E-HORO` (horodatage P3), `E-FORM` (saisie/formulaire), `E-SYS` (panne
système/offline), `E-MAT` (matériel/UDI), `E-SAE` (report de sécurité),
`E-PROC` (procédure locale).

**Règles de classement** :
- **Majeure** = affecte droits, sécurité ou bien-être du participant ; ou
  fiabilité des endpoints primaires (κ pondéré, délai P3, sûreté 30 j) ;
  ou rupture de la chaîne d'audit.
- **Mineure** = écart de process sans impact participant/endpoints
  (ex. rapport signé à J+6).
- Une déviation majeure répétée sur un même site → visite ad hoc sous
  2 semaines (plan-monitoring §2) et rapport au DSMB avec proposition
  (suspension d'inclusion du site, reformation, exclusion du site).

**Verrouillage de la base (M+18)** : aucune déviation ouverte (CAL non
clôturée) ne doit subsister au lock — le promoteur vérifie ce registre avant
`POST /api/v1/ecrf/study/lock` ; les déviations résiduelles sont documentées
dans le rapport d'investigation (MEDDEV 2.7/1 rev 4, R7) avec leur impact
sur les endpoints.
