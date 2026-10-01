# syntax=docker/dockerfile:1

# HOMA — Hands-On Machine Assistant
# The Playwright base image ships Chromium plus every system library it needs.
FROM mcr.microsoft.com/playwright/python:v1.63.0-jammy

LABEL org.opencontainers.image.title="HOMA" \
      org.opencontainers.image.description="Self-hosted, local-first AI agent that drives a real browser, controls your computer, reads mail, remembers, and runs scheduled tasks." \
      org.opencontainers.image.source="https://github.com/sadult/homa" \
      org.opencontainers.image.licenses="PolyForm-Noncommercial-1.0.0" \
      org.opencontainers.image.authors="Mersad Shahidi"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HEADLESS=true \
    WEB_HOST=0.0.0.0 \
    WEB_PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/downloads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/').status==200 else 1)"

CMD ["python", "main.py", "both"]
