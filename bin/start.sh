#!/usr/bin/env bash
set -e

echo "[start] kicking off background collectors..."

# Run everything non-critical in the background with soft-fail
( python pipelines/rss_collect.py || echo "[warn] RSS collection failed" ) &
( [ -n "$YOUTUBE_API_KEY" ] && python pipelines/youtube_collect.py || echo "[info] skipping YouTube" ) &
( python pipelines/normalize.py || echo "[warn] normalize failed" ) &

# Build DB/vectors in the background too (first response can be empty; that's fine)
python - <<'PY' || echo "[warn] DB/vector build failed (will serve anyway)"
from app.store import init, load_processed, init_vectors, upsert_vectors
c = init(); load_processed(c); coll = init_vectors(); upsert_vectors(coll)
print("DB + vectors ready")
PY

echo "[start] launching API on 0.0.0.0:${PORT:-8000}"
# Exec replaces shell so container lifecycle is tied to uvicorn
exec uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}
