"""
Configuration de l'environnement Alembic pour les migrations de base de données.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ajout du répertoire des migrations au PYTHONPATH
migrations_dir = os.path.dirname(os.path.abspath(__file__))
if migrations_dir not in sys.path:
    sys.path.insert(0, migrations_dir)

from models import Base

# Lecture de la configuration Alembic
config = context.config

# Configuration du logging depuis alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Modèles à utiliser pour les migrations
target_metadata = Base.metadata

def get_url():
    """Construit l'URL de connexion à partir des variables d'environnement."""
    return "postgresql://postgres:postgres@localhost:5432/auth_db"

def run_migrations_offline() -> None:
    """
    Exécute les migrations en mode "offline".
    
    Ce mode génère les commandes SQL dans un fichier au lieu de les exécuter directement.
    Utile pour la revue des changements ou l'exécution manuelle.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Exécute les migrations en mode "online".
    
    Ce mode exécute les migrations directement sur la base de données.
    C'est le mode par défaut pour les environnements de développement et production.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Options supplémentaires pour le contrôle des migrations
            compare_type=True,  # Compare les types de colonnes
            compare_server_default=True,  # Compare les valeurs par défaut
            include_schemas=True,  # Inclut tous les schémas
            version_table_schema=target_metadata.schema,  # Schéma pour la table de version
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
