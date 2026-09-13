# CHANGE_CLASSIFICATION — classes P0 à P9

| Classe | Nature | Exemple | Approbation | Régression complète |
|---|---|---|---|---|
| P0 | interdit | violation sécurité/sûreté | — (blocage) | — |
| P1 | documentaire | README | aucune | non |
| P2 | maintenance | refactoring sans comportement | aucune | non |
| P3 | feature non-breaking | nouveau module | simple | non |
| P4 | architecture | nouveau service/contrat | simple + sécurité | oui |
| P5 | données | migration DB | double (tech + DPO) | oui |
| P6 | IA | nouveau modèle/seuil | double (tech + clinique) | oui |
| P7 | clinique | règle/score clinique | double (clinique + sûreté) | oui |
| P8 | sécurité patient | décisionnelle, safety gate | comité | oui |
| P9 | réglementaire | impact conformité MDR | comité | oui |

**Plus la classe monte, plus les gates humaines et de validation sont fortes.**

Détection automatique : règles de chemins dans `change-types.yaml`
(`packages/clinical-rules/**` → P7, `ai/**` → P6, `migrations/**` → P5, etc.).
La classe détectée est un **plancher** : l'analyse d'impact peut la remonter, jamais l'abaisser.
