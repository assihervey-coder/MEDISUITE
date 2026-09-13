# Gouvernance MEDISUITE

- `evolution/` — politiques du cycle d'évolution (classification P0-P9, approbation, rollback, compatibilité, politiques clinique/IA/données/sécurité/réglementaire)
- `proposals/` — templates de propositions + **registry** (`proposals.yaml`, source de vérité des PROP-*)
- `adr/` — ADRs du control plane (active/accepted/rejected/superseded) — les ADRs plateforme restent dans `docs/adr/`
- `architecture/` — baseline / target / snapshots / diffs

Toute décision produit une **preuve** (`evidence/evolution/`) et un événement d'audit
immuable (`audit/evolution/`, chaîne de hachage).
