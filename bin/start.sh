#!/usr/bin/env bash
set -e

echo "[start] collecting RSS..."
python pipelines/rss_collect.py || echo "[warn] RSS collection failed; continuing..."

if [ -n "$YOUTUBE_API_KEY" ]; then
  echo "[start] collecting YouTube..."
  python pipelines/youtube_collect.py || echo "[warn] YouTube collection failed; continuing..."
else
  echo "[start] YOUTUBE_API_KEY not set; skipping YouTube collection."
fi

echo "[start] normalizing..."
python pipelines/normalize.py || echo "[warn] Normalize failed; continuing..."

echo "[start] building DB + vectors..."
python - <<'PY' || echo "[warn] DB/vector build failed; continuing to serve API..."
from app.store import init, load_processed, init_vectors, upsert_vectors
c = init(); load_processed(c); coll = init_vectors(); upsert_vectors(coll)
print("DB + vectors ready")
PY

echo "[start] launching API on 0.0.0.0:${PORT:-8000}"
exec uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}
