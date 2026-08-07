# ── Stage 1: Builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# System deps needed to *build* some wheels (psycopg2, cryptography, lxml…)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Runtime system deps:
#   tesseract-ocr  → pytesseract
#   libnss3 + friends → Playwright Chromium
#   libpq5         → psycopg2 at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Install Playwright browsers (Chromium only — saves ~600 MB vs all browsers)
RUN playwright install chromium

COPY . .

# Non-root user — never run prod containers as root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# ── NO --reload in production ────────────────────────────────────────────────
# Workers = (2 × CPU cores) + 1  →  adjust to your droplet size
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
