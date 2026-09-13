# CLINICAL_CHANGE_POLICY

Toute proposition clinique déclenche automatiquement :

```
Clinical Proposal → Clinical Impact Assessment
   (patient safety · workflow · règle clinique · contre-indication ·
    alerte · recommandation · decision support)
→ Clinical Validation → Safety Review → Human Approval
```

- Classe plancher P7 ; impact décisionnel (ce que le clinicien voit/reçoit) → P8.
- La validation exige une cohorte rétrospective sur datasets référencés
  (`datasets/registry.py`) AVANT tout passage en PILOT.
- Les scores/paramètres modifiés doivent citer leur référentiel (convention
  packages/clinical-rules) et mettre à jour les model-cards concernées.
- Chaque changement de règle est rejouable : les tests `packages/clinical-rules/tests`
  verrouillent les cas limites documentés.
