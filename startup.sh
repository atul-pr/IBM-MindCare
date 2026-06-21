#!/bin/bash
set -e

echo "=== HealSpace AI Startup ==="
echo "Python: $(python --version)"
echo "Working dir: $(pwd)"
echo "PORT: $PORT"
echo "FLASK_ENV: $FLASK_ENV"
echo "HF_HOME: $HF_HOME"

echo ""
echo "--- Testing imports ---"
python -c "import flask; print('Flask OK:', flask.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy OK:', sqlalchemy.__version__)"
python -c "import faiss; print('FAISS OK')"
python -c "import sentence_transformers; print('SentenceTransformers OK:', sentence_transformers.__version__)"
python -c "import groq; print('Groq OK:', groq.__version__)"
python -c "import gevent; print('Gevent OK:', gevent.__version__)"

echo ""
echo "--- Starting gunicorn ---"
exec gunicorn app:app \
    --workers=1 \
    --timeout=120 \
    --bind=0.0.0.0:${PORT:-8080} \
    --log-level=debug \
    --access-logfile=- \
    --error-logfile=-
