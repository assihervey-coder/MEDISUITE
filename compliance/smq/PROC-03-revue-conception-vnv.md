# PROC-03 — Revue de conception, vérification et validation (ISO 13485 §7.3, IEC 62304)

**Propriétaire** : Ingénierie + RQ | **Revue** : à chaque jalon de conception | **Version** : 1.0

## 1. Finalité

Formaliser les revues de conception exigées par la classe de sécurité **C**
(IEC 62304) — aujourd'hui informelles (ADRs + tests) — en enregistrements
signés exploitables par l'organisme notifié.

## 2. Jalons de revue

| Jalon | Entrées | Sorties signées |
|---|---|---|
| R1 — spécifications | EGSP, besoins cliniques, référentiels | rapport de spécification (matrice exigence↔source) |
| R2 — architecture | ADRs, diagrammes, contrats de service | PV de revue d'architecture (risques RM-* cités) |
| R3 — risque | FMEA mise à jour | PV d'acceptabilité (comité des risques) |
| R4 — V&V | plans/rapports de test, usabilité | rapport de V&V par version |
| R5 — libération | checklist PROC-07 | décision de libération |

## 3. Règles de V&V

1. **Vérification** : chaque exigence EGSP a ≥ 1 preuve de test automatisé
   ou un plan de vérification manuel daté (373+ tests actuels, 4 niveaux —
   cf. dossier CE §6.3).
2. **Validation** : usabilité (IEC 62366 — protocole `usability/`),
   investigation clinique multicentrique (Annexe XV), banc de performance
   (`tools/bench/`, critère p95 ≤ 2 s).
3. **Reproductibilité** : tout test doit pouvoir être rejoué en CI sur
   environnement frais (contrainte déjà implémentée : BDD fraîche par run).
4. **Unités critiques** : `clinical-rules` (90+ scores), `FusionEngine`,
   `audit_chain`, `rbac` — couverture cible ≥ 80 %, mesurée et archivée à
   chaque release (écart : mesure non archivée → à instaurer, jalon R4).

## 4. Enregistrements & indicateurs

- PV de revue (participants, écarts, décisions) — stockés dans l'archive
  qualité, référencés depuis les ADRs correspondants.
- Indicateurs : % exigences EGSP prouvées (cible 100 % à v1.0) ; nb d'écarts
  de conception détectés/en revue (indicateur de maturité, pas de blâme).
