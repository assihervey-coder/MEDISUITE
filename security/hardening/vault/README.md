# HashiCorp Vault — gestion des secrets (jalon R4, RGPD art. 32)

> Statut : intégration préparée v0.5 (dev/test) — production : cluster Vault
> HA + transit seal à définir avec le CHU. **Aucun secret applicatif ne doit
> rester en variable d'environnement en production.**

## 1. Architecture cible

```
┌─────────────────┐   AppRole/Token    ┌────────────────────────┐
│ services MEDISU. │──────────────────▶│ vault:8200 (KV v2)     │
│ (38 services)    │                   │ secret/medisuite/{env}/│
└─────────────────┘                    │  orthanc, fhir, db, jwt│
                                       └──────────┬─────────────┘
                                                  │ audit device (file)
                                                  ▼ logs d'accès aux secrets
```

## 2. Démarrage local (dev)

```bash
# service déjà ajouté au compose (mode dev, UI :9000, VAULT_DEV_ROOT_TOKEN à changer)
docker compose -f local-deployment/docker-compose.minimal.yml up -d vault
export VAULT_ADDR=http://localhost:9000
export VAULT_TOKEN=<root-token-dev>          # dev uniquement
bash security/hardening/vault/init_secrets.sh
```

Le script `init_secrets.sh` :
1. active le moteur KV v2 sur `secret/` ;
2. écrit les chemins `secret/medisuite/local/{orthanc,fhir,jwt,db}` à partir
   des valeurs de dev actuelles (parité avec le compose) ;
3. crée la policy `medisuite-services` (lecture restreinte, chemin par
   environnement, `list` interdit) ;
4. active l'audit device file (traçabilité des lectures de secrets).

## 3. Policies (principe du moindre privilège)

`security/hardening/vault/policies/medisuite-services.hcl` — un service ne
peut lire que `secret/medisuite/<env>/<composant>` ; la suppression est
interdite aux services ; la rotation requiert une entité humaine
(ASVS 2.6/2.7 : durées de vie courtes, rotation documentée).

## 4. Migration applicative (ordre prévu, v0.6)

1. `medisuite_core/security.py` : `load_secret(name)` — lit Vault si
   `MEDISUITE_VAULT_ADDR` est défini, sinon fallback env (dev) ;
2. rotation JWT_SECRET : double-lève (ancien+nouveau) puis bascule ;
3. retrait progressif des secrets du compose (le compose de prod ne garde
   QUE le token AppRole bootstrap, court-lived).

## 5. Limites honnêtes

- Le mode `-dev` du compose est **non persistant et non scellé** : il sert à
  outiller la migration, pas la production.
- Le sealing transit (auto-unseal KMS) et HA (Raft) sont hors périmètre v0.5.
- Rotation automatique des secrets de BDD (dynamic secrets) : v0.6.
