#!/usr/bin/env bash
# init_secrets.sh — initialise Vault (KV v2 + policy + audit) avec les
# secrets de DÉVELOPPEMENT par parité avec docker-compose. Dev/local ONLY.
set -euo pipefail

: "${VAULT_ADDR:?exporter VAULT_ADDR (ex. http://localhost:9000)}"
: "${VAULT_TOKEN:?exporter VAULT_TOKEN}"

vault_cmd() { curl -s -H "X-Vault-Token: $VAULT_TOKEN" "$@"; }
BASE="$VAULT_ADDR/v1"

echo "== 1. Activation moteur KV v2 sur secret/ =="
vault_cmd -X POST "$BASE/sys/mounts/secret" -d '{
  "type": "kv", "options": {"version": "2"},
  "description": "MEDISUITE secrets (KV v2)"}' > /dev/null || true

echo "== 2. Écriture des secrets de dev =="
put() { # put <chemin> <json>
  vault_cmd -X POST "$BASE/secret/data/$1" -d "{\"data\": $2}" > /dev/null
}
put medisuite/local/orthanc '{"user":"medisuite","password":"medisuite-dev"}'
put medisuite/local/fhir    '{"base":"http://hapi-fhir:8080/fhir"}'
put medisuite/local/jwt     '{"secret":"medisuite-dev-secret-change-in-prod"}'
put medisuite/local/db      '{"url":"sqlite:///dev/null","note":"parité dev"}'

echo "== 3. Policy medisuite-services =="
POLICY=$(cat "$(dirname "$0")/policies/medisuite-services.hcl")
vault_cmd -X PUT "$BASE/sys/policies/acl/medisuite-services" \
  -d "$(python3 -c 'import json,sys;print(json.dumps({"policy":sys.stdin.read()}))' <<< "$POLICY")" > /dev/null

echo "== 4. Audit device (file) =="
vault_cmd -X POST "$BASE/sys/audit/file" \
  -d '{"type":"file","options":{"file_path":"/vault/logs/audit.log"}}' > /dev/null || true

echo "OK — Vault initialisé (dev). Lire un secret :"
echo "  curl -s -H 'X-Vault-Token: \$VAULT_TOKEN' $BASE/secret/data/medisuite/local/orthanc"
