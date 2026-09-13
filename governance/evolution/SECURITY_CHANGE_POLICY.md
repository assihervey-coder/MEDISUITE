# SECURITY_CHANGE_POLICY

Classe plancher P8 pour tout ce qui touche à : authentification, autorisation,
chiffrement, piste d'audit, réseau (mTLS, NetworkPolicy), secrets (Vault).

- Threat model mis à jour obligatoirement (`security/hardening/`).
- Toute évolution du réseau k8s doit préserver le **default-deny** (v0.15.0) :
  une allowlist nouvelle passe par proposition avec justification.
- Pentest externe : classé terrain R3 — les correctifs qui en découlent
  reviennent comme propositions SECURITY.
- Clés/PAT : rotation périodique ; aucun secret dans le dépôt (CI le verrouille).
