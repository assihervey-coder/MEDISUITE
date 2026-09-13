# Feature Flags (control plane de release)

- `definitions/` — registre des flags (owner, proposal liée, type, TTL)
- `environments/{dev,staging,pilot,production}/` — état par environnement
- `policies/` — règles de progression OFF → DEV → STAGING → PILOT → CANARY → 10% → 25% → 50% → 100%

Aucun flag sans proposition liée ; TTL max 90 jours (nettoyage contrôlé).
