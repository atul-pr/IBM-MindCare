# Use slim Python 3.11 — no Nix complications, proven on Railway
FROM python:3.11-slim

WORKDIR /app

# Set env vars at build time
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CUDA_VISIBLE_DEVICES=-1 \
    HF_HOME=/app/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/app/hf_cache \
    TF_CPP_MIN_LOG_LEVEL=3

# Install system build dependencies for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    cmake \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch FIRST (700MB vs 5GB CUDA build)
RUN pip install --no-cache-dir \
    "torch==2.2.2+cpu" \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Copy and install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Pre-download the embedding model into /app/hf_cache (baked into image = instant startup)
RUN python -c "\
import os; \
os.environ['HF_HOME'] = '/app/hf_cache'; \
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/app/hf_cache'; \
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2', cache_folder='/app/hf_cache'); \
print('Embedding model pre-downloaded successfully')" \
    || echo "Model pre-download skipped — will download at first request"

EXPOSE 8080

CMD ["gunicorn", "app:app", "--workers=1", "--timeout=120", "--bind=0.0.0.0:8080", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]
