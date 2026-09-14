#!/usr/bin/env bash
PORT="${TROPIRAG_PORT:-8000}"
python3 -c "import httpx;r=httpx.get('http://localhost:$PORT/api/v1/health',timeout=5);print(r.json()['status']);r.raise_for_status()"
