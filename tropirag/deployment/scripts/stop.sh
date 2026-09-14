#!/usr/bin/env bash
pkill -f "uvicorn tropirag.api.app" 2>/dev/null && echo "arrêté" || echo "aucun processus"
