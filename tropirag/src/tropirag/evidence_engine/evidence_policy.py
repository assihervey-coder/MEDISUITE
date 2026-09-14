"""Politique de preuve — règles de citation et de conflit."""

POLICIES = {
    "citation_required": True,          # toute affirmation clinique cite son unité
    "no_evidence_no_synthesis": True,   # pas de preuve → pas de synthèse IA
    "authority_precedence": ["who", "national", "msf", "cdc", "institutional", "scientific"],
    "conflict_resolution": "l'unité de rang d'autorité inférieur cède ; conflit OMS↔national documenté",
    "temporal_precedence": "l'édition la plus récente d'une même autorité prime",
    "min_units_for_synthesis": 1,
}
