# Policy Vault MEDISUITE — services applicatifs (moindre privilège)
# Lecture seule sur son environnement ; list et delete interdits ;
# les écritures/rotations sont réservées à une entité humaine
# (policy medisuite-admin, délivrée via SSO/authentification forte).
#
# NOTE v0.5 : la référence par alias AppRole (identity.entity.aliases…)
# nécessite un auth backend AppRole configuré ; en dev, utiliser la
# policy plate ci-dessous (commentée) pour les tests manuels.
path "secret/data/medisuite/local/*" {
  capabilities = ["read"]
}

# Méta (versions, métadonnées) en lecture — utile aux checks de rotation
path "secret/metadata/medisuite/*" {
  capabilities = ["read"]
}

# Aucun accès service à la zone admin — écritures/rotations humaines
path "secret/data/medisuite/admin/*" {
  capabilities = []
}
