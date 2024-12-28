"""Configuration de l'environnement Alembic."""

from logging.config import fileConfig
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine

# Ajoute le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.core.base import Base
from app.core.config import settings
from app.models import *  # Importe tous les modèles

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    """Récupère l'URL de la base de données depuis les paramètres."""
    url = config.get_main_option("sqlalchemy.url")
    if url:
        return url
    return str(settings.SQLALCHEMY_DATABASE_URI)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Utilise directement create_engine au lieu de engine_from_config
    # pour avoir plus de contrôle sur la configuration
    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        echo=settings.DEBUG
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 