#!/usr/bin/env bash
# gen_certs.sh — PKI interne de TEST pour mTLS MEDISUITE (openssl stdlib).
# Usage : bash gen_certs.sh <domaine-base>   (ex. medisuite.local)
# Sortie : out/{ca,server,client-*}.{crt,key} — JAMAIS en production.
set -euo pipefail
DOMAIN="${1:?usage: gen_certs.sh <domaine-base>}"
OUT="$(dirname "$0")/out"; mkdir -p "$OUT"; cd "$OUT"

echo "== AC racine (10 ans) =="
openssl genrsa -out ca.key 4096 2>/dev/null
openssl req -x509 -new -key ca.key -sha256 -days 3650 -subj "/CN=MEDISUITE Test CA/O=Medisuite" -out ca.crt

echo "== Serveur (1 an, SAN multi-hôtes) =="
openssl genrsa -out server.key 2048 2>/dev/null
cat > server.cnf <<EOF
[req]
distinguished_name=dn
req_extensions=v3_req
prompt=no
[dn]
CN=*.${DOMAIN}
O=Medisuite
[v3_req]
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:hapi-fhir,DNS:orthanc-pacs,DNS:api-gateway,DNS:*.${DOMAIN},DNS:localhost
EOF
openssl req -new -key server.key -out server.csr -config server.cnf
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 365 -sha256 -extfile server.cnf -extensions v3_req -out server.crt 2>/dev/null

echo "== Clients (1 an, EKU clientAuth) =="
mk_client() { # mk_client <nom>
  openssl genrsa -out "client-$1.key" 2048 2>/dev/null
  openssl req -new -key "client-$1.key" -subj "/CN=$1/O=Medisuite-Clients" -out "client-$1.csr"
  printf "basicConstraints=CA:FALSE\nkeyUsage=digitalSignature\nextendedKeyUsage=clientAuth\n" > "client-$1.ext"
  openssl x509 -req -in "client-$1.csr" -CA ca.crt -CAkey ca.key -CAcreateserial \
    -days 365 -sha256 -extfile "client-$1.ext" -out "client-$1.crt" 2>/dev/null
}
mk_client integration
mk_client webportal

echo "OK — certificats dans $(pwd)"
openssl verify -CAfile ca.crt server.crt client-integration.crt client-webportal.crt
