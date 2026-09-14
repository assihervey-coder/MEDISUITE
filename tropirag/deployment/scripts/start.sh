#!/usr/bin/env bash
cd "$(dirname "$0")/../.."
exec python3 -m uvicorn tropirag.api.app:app --host 0.0.0.0 --port "${TROPIRAG_PORT:-8000}"
