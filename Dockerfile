# Backend image: FastAPI + FAISS + local embedding model.
# Works on Hugging Face Spaces (sdk: docker), Render, Railway, and Fly.io.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# CPU-only torch first: the default wheel bundles CUDA and is several GB larger.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY artifacts/ artifacts/

# Bake the embedding model and FAISS index into the image so cold starts are fast.
# The placeholder key only satisfies config validation during the build; the real
# ANTHROPIC_API_KEY is supplied at runtime.
RUN ANTHROPIC_API_KEY=build-placeholder python -m backend.scripts.ingest

EXPOSE 7860
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
