FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm

COPY . .

# Render/Fly set PORT; default to 8000
ENV PORT=8000
EXPOSE 8000

# Start script runs collection once, builds DB, then starts API
RUN chmod +x bin/start.sh
CMD ["bash", "bin/start.sh"]
