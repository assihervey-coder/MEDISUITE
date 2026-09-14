#!/usr/bin/env bash
cd "$(dirname "$0")/../.."
mkdir -p db/backups
tar czf "db/backups/tropirag-$(date +%Y%m%d-%H%M%S).tar.gz" db/tropirag.sqlite3 2>/dev/null || echo "rien à sauvegarder"
echo "sauvegarde → db/backups/"
