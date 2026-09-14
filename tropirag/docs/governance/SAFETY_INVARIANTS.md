# Invariants de sécurité (implémentés et testés)

| # | Invariant | Implémentation | Test |
|---|-----------|----------------|------|
| G1 | Un red flag ne peut jamais être retiré | SafetyEngine consolide, ResponseBuilder affiche en tête | tests/safety |
| G2 | Aucune sortie sans disclaimer | ClinicalResponse.disclaimer obligatoire | tests/clinical |
| G3 | Pas de preuve → pas de synthèse IA | EvidenceGuard + SafetyGate | tests/safety |
| G4 | Aucune posologie générée par IA | DOSE_PATTERNS + guards | tests/safety |
| G5 | Cas critique → déterministe pur | RiskRouter + SafetyGate | tests/safety |
| G6 | Diagnostic autonome interdit | AutonomousDiagnosisGuard (formulations verrouillées) | tests/safety |
| G7 | Notifications santé publique préservées | RuleEngine pass 3 | tests/clinical |
| — | Injection de prompt rejetée | InputGuard | tests/adversarial |
| — | Hallucination non ancrée rejetée | HallucinationGuard (overlap sur unité citée) | tests/adversarial |
| — | AINS bloqués en contexte dengue | Drug Engine déterministe | tests/safety |
| — | Isolement + RSI sur suspicion MVH | Règles hcid/* | tests/clinical |

## Preuve continue

Le benchmark de sécurité (`scripts/evaluate_safety.py`) est exécuté dans la CI
à chaque push : toute régression d'invariant casse le build.
