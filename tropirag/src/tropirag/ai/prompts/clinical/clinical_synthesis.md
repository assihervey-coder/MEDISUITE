# Synthèse clinique (Med42)

## CONTEXT
{{CONTEXT}}

## EVIDENCE (sources autoritaires — citer sous la forme [eu-...])
{{EVIDENCE}}

## CONSTRAINTS (inviolables)
{{CONSTRAINTS}}

À partir du CONTEXTE et des PREUVES ci-dessus, produire une synthèse JSON :

{
  "summary": "3 à 6 phrases en français, chaque affirmation clinique citée [eu-...]",
  "key_findings": ["..."],
  "differential_review": ["commentaire sur chaque hypothèse, cohérent avec les règles"],
  "warnings": ["signes d'alarme rappelés"],
  "citations": ["eu-xxx utilisées"]
}

Interdits : diagnostic certain, posologie, contredit un red flag.
