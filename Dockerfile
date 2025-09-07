FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Upgrade pip first (still small)
RUN pip install --upgrade pip

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# App port
ENV PORT=8000
EXPOSE 8000

# Start: collect (soft-fail), normalize, build DB, serve API
RUN chmod +x bin/start.sh
CMD ["bash", "bin/start.sh"]
