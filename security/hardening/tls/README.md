# TLS / mTLS — chiffrement des flux internes et externes (jalon R4)

> Statut : outillage prêt v0.5 (PKI interne de test) — production :
> PKI du CHU ou AC interne certifiée ; rotation automatisée GitOps.

## 1. Objectif (RGPD art. 32, EGSP §17.2)

- TLS 1.2+ partout au bord (ingress) : terminaison NGINX/ingress.
- **mTLS entre services sensibles** : hub FHIR → HAPI, gateways → services
  (l'identité du client est vérifiée par certificat, pas par secret partagé).

## 2. Génération d'une PKI de test

```bash
bash security/hardening/tls/gen_certs.sh medisuite.local
# produit security/hardening/tls/out/ :
#   ca.crt / ca.key (AC interne de test)
#   server.crt (SAN DNS hapi-fhir, orthanc-pacs, api-gateway…)
#   client-integration.crt (identité client du hub FHIR)
#   client-webportal.crt
```

`gen_certs.sh` (openssl stdlib) : AC racine 4096 bits (10 ans), serveur +
clients 2048 bits (1 an), SAN complètes, extensions EKU serverAuth /
clientAuth distinctes — un certificat client ne peut pas servir de serveur
et inversement.

## 3. Application mTLS — exemple HAPI derrière NGINX

`security/hardening/tls/nginx-mtls.conf` : listener 8443 ssl + `ssl_verify_client on`
(AC interne) + proxy vers `hapi-fhir:8080`. Le conteneur HAPI n'est plus
exposé que via ce proxy : `ssl_client_certificate = ca.crt`.

En Kubernetes : remplacer par service mesh (Linkerd/Istio mTLS) ou
NetworkPolicy + ingress TLS — décision ADR à prendre au jalon R8 selon
l'infrastructure CHU.

## 4. Checklist de durcissement TLS (OWASP ASVS §9)

- [x] TLS 1.2 minimum, suites ECDHE+AESGCM uniquement (script `ssl_conf`)
- [x] HSTS à l'ingress (`Strict-Transport-Security: max-age=63072000`)
- [ ] AC de production + rotation automatique (jalon R8)
- [ ] Tests d'intrusion des flux (plan `../pentest/`)
- [x] Pas de secret dans les URLs ni les logs (audit chaîné sans payload)

## 5. Limites honnêtes

La PKI de test n'est pas une AC de production ; le compose local reste en
HTTP pour le dev (documenté) ; la bascule mTLS complète des 38 services
exige l'orchestrateur (K8s) — côté compose, seul le couple FHIR/HAPI est
démontré.
