# Workflow clinique — fièvre + voyage

1. **Saisie** : âge, sexe, grossesse, symptômes (texte libre FR), pays visités,
   dates de voyage, constantes, biologie disponible.
2. **Normalisation** : texte libre → codes canoniques (fièvre 39,6 → high_fever).
3. **Expositions** : segments de voyage → palu/dengue/YF/MVH/Lassa par géoprofil.
4. **Règles** (3 passes) : suspicions → red flags → actions (tests, contraintes,
   escalade, notifications).
5. **Temporel** : fenêtres d'incubation (palu 7-90 j, dengue 3-14 j, Ebola 2-21 j...).
6. **Différentiel** : pondération explicable (règle × poids), must-not-miss en tête.
7. **Preuves** : retrieval hybride + citations obligatoires.
8. **Synthèse IA** (si autorisée) : Med42 sous contrat, auditée par R1.
9. **Safety Gate** : G1-G7 — décision finale de sortie.
10. **Réponse** : narrative structurée, différentiel, red flags, examens,
    contre-indications, citations, provenance complète, disclaimer.
