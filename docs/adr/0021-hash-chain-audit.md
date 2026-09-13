# ADR-0021 — Registre d'audit à chaîne de hachage (pas blockchain)

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Une blockchain complète pour l'audit est sur-engineerée (coût, latence, complexité opérationnelle).

## Décision
Chaîne SHA-256 {index, prev_hash, payload, ts} + vérification d'intégrité : mêmes garanties de non-répudiation, 100× plus simple.

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
