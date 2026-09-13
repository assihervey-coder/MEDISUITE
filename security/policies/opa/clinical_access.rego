package medisuite.clinical_access

# Autorisation clinique fine (RBAC médical) — évaluée par l'OPA sidecar.
default allow = false

allow {
    input.role == "medecin"
    input.permission in {"patient.read", "patient.write", "ai.infer", "lab.order"}
}

allow {
    input.role == "biologiste"
    input.permission in {"lab.order", "lab.validate", "lab.qc"}
}

allow {
    input.role == "administrateur"
    input.permission == "audit.read"
}

# Interdiction absolue : un patient ne consulte jamais le dossier d'un autre
deny {
    input.role == "patient"
    input.permission in {"patient.read", "ai.infer"}
}
