# =====================================================
# Builder
# =====================================================

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements ./requirements

RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements/all.txt


# =====================================================
# Runtime
# =====================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system appgroup && \
    adduser --system appuser --ingroup appgroup

COPY --from=builder /install /usr/local

COPY . .

# Ensure the migrate-then-serve entrypoint is executable, then drop privileges.
RUN chmod +x /app/docker-entrypoint.sh && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/health')"

# Schema is owned by Alembic: the entrypoint runs `alembic upgrade head`
# BEFORE starting uvicorn, so deployments are deterministic and the app never
# creates tables at runtime.
ENTRYPOINT ["/app/docker-entrypoint.sh"]

