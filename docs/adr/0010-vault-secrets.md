# ADR-0010 — HashiCorp Vault pour les secrets

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Les .env committés sont la première cause de fuite (constaté dans la spec d'origine).

## Décision
Vault en prod ; dev : .env.example + secrets/ gitignorés ; rotation scriptée rotate-secrets.sh.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
