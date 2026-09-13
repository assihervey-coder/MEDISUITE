# EVOLUTION_LIFECYCLE — machine à états

```
DRAFT → SUBMITTED → VALIDATED → CLASSIFIED → IMPACT_ANALYSIS → RISK_ASSESSMENT
      → DECISION_PENDING ─┬→ REJECTED (terminal)
                          ├→ DEFERRED (réactivable → VALIDATED)
                          └→ APPROVED → CHANGE_PLANNED → IMPLEMENTATION
      → TECHNICAL_VALIDATION → CLINICAL_VALIDATION → SAFETY_VALIDATION
      → RELEASE_CANDIDATE → CANARY → PILOT → ROLLOUT
      → RELEASED → MONITORED → ACCEPTED (nouvelle baseline)
```

**Transverses** : ROLLOUT → PAUSED (reprise possible) ; ROLLOUT → ROLLED_BACK
(retour à la baseline précédente, terminal après vérification + preuve).

## Garde-fous (implémentés dans `domain/proposal/policies.py`)
1. Toute transition non listée est refusée (`strict: true`).
2. Une classe P5+ ne franchit pas TECHNICAL_VALIDATION sans rapport de compatibilité.
3. Une classe P7+ ne franchit pas CLINICAL_VALIDATION sans revue signée.
4. Les classes P8/P9 exigent le quorum complet du comité (voir APPROVAL_POLICY).
5. Chaque transition émet un événement `audit/evolution/` avec `previous_state`,
   `new_state`, `actor`, `reason`, `evidence_id` — append-only.
