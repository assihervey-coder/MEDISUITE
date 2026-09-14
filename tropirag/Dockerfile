# TropiRAG — image API (mode déterministe par défaut)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY configs/ ./configs/
COPY rules/ ./rules/
COPY corpus/ ./corpus/
COPY prompts/ ./prompts/
COPY scripts/ ./scripts/

RUN pip install -e ".[api]"

# base de données runtime
RUN mkdir -p /app/db /app/runtime/logs

ENV TROPIRAG_ROOT=/app TROPIRAG_INFERENCE_MODE=deterministic
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import httpx;httpx.get('http://localhost:8000/api/v1/health',timeout=4).raise_for_status()"

CMD ["python", "-m", "uvicorn", "tropirag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
