# Stage de build
FROM python:3.10-slim as builder

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Configuration du projet
WORKDIR /app
COPY pyproject.toml ./

# Installation des dépendances
RUN poetry install --only main --no-root

# Stage final
FROM python:3.10-slim as runner

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Configuration du projet
WORKDIR /app

# Copie de l'environnement virtuel
COPY --from=builder /app/.venv ./.venv

# Copie du code source et des fichiers de migration
COPY app app/
COPY alembic.ini .
COPY migrations migrations/

# Création de l'utilisateur non-root
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser && \
    chown -R appuser:appuser /app

# Configuration de l'environnement
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

# Passage à l'utilisateur non-root
USER appuser

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
