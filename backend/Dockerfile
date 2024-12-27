# Build stage
FROM python:3.10-slim AS builder

# Configuration des variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Installation des dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        postgresql-client \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Copie des fichiers de dépendances
COPY pyproject.toml poetry.lock* ./

# Installation des dépendances
RUN poetry install --no-dev --no-root

# Production stage
FROM python:3.10-slim AS runner

# Configuration des variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Installation des dépendances système minimales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des dépendances et du code
COPY --from=builder /app/.venv ./.venv
COPY . .

# Création d'un utilisateur non-root
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exposition du port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
