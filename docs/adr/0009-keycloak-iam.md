# ADR-0009 — Keycloak pour l'identité, auth-service comme abstraction

**Statut :** accepté · **Date :** 2026-09-13 · **Décideurs :** architecture MEDISUITE

## Contexte
Implémenter OAuth2/OIDC complet maison est risqué (IEC 62304).

## Décision
auth-service fournit JWT/MFA/RBAC maison auditable ET s'intègre Keycloak/LDAP (adapters).

## Conséquences
- Positive : cohérence globale, auditabilité, coût de possession réduit.
- Vigilance : chaque écart à cette décision exige un nouvel ADR (processus documenté).
- Traçabilité : décision alignée avec l'audit d'architecture du 2026-09 (risques R1-R10).
