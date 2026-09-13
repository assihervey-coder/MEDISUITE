# Audit trail (append-only)

- `evolution/` — événements du cycle de vie des propositions (JSONL chaîné SHA-256)
- `approvals/`, `deployments/`, `rollbacks/`, `evidence/` — événements spécialisés

**Immuabilité** : chaque enregistrement porte `previous_hash` ; toute altération casse la chaîne
(vérifié par `evolution-control-plane/domain/proposal/../audit` → `verify_chain()` dans les tests).
