"""
Script d'installation et de configuration de la base de données PostgreSQL.
Utilise Docker et notre nouvelle architecture de base de données.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_docker_installed():
    """Vérifie si Docker est installé et en cours d'exécution."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Docker ou docker-compose n'est pas installé.")
        return False

def check_env_file():
    """Vérifie et crée le fichier .env si nécessaire."""
    env_path = Path(__file__).parent.parent.parent / ".env"
    env_example_path = Path(__file__).parent.parent.parent / ".env.example"

    if not env_path.exists():
        if env_example_path.exists():
            logger.info("Création du fichier .env à partir de .env.example")
            with open(env_example_path, 'r') as example, open(env_path, 'w') as env:
                env.write(example.read())
        else:
            logger.info("Création d'un nouveau fichier .env")
            env_content = """
DB_HOST=db
DB_PORT=5432
DB_NAME=auditronai
DB_USER=postgres
DB_PASSWORD=postgres
            """.strip()
            with open(env_path, 'w') as f:
                f.write(env_content)

def start_database():
    """Démarre les conteneurs Docker."""
    try:
        project_root = Path(__file__).parent.parent.parent
        logger.info("Démarrage des conteneurs Docker...")
        subprocess.run(
            ["docker-compose", "up", "-d", "db"],
            check=True,
            cwd=str(project_root)
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du démarrage des conteneurs: {e}")
        return False

def wait_for_database():
    """Attend que la base de données soit prête."""
    max_retries = 30
    retry_interval = 2

    logger.info("Attente de la disponibilité de la base de données...")
    for i in range(max_retries):
        try:
            subprocess.run(
                ["docker-compose", "exec", "db", "pg_isready", "-U", "postgres"],
                check=True,
                capture_output=True
            )
            logger.info("Base de données prête !")
            return True
        except subprocess.CalledProcessError:
            if i < max_retries - 1:
                time.sleep(retry_interval)
            else:
                logger.error("La base de données n'est pas devenue disponible à temps.")
                return False

def setup_database():
    """Configure la base de données avec Alembic."""
    try:
        project_root = Path(__file__).parent.parent.parent
        migrations_dir = project_root / "AuditronAI" / "core" / "database" / "migrations"
        
        # Exécute la migration initiale
        logger.info("Application des migrations de base de données...")
        subprocess.run(
            [sys.executable, "manage_migrations.py", "upgrade", "head"],
            check=True,
            cwd=str(migrations_dir)
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la configuration de la base de données: {e}")
        return False

def main():
    """Fonction principale d'installation."""
    logger.info("Démarrage de l'installation de la base de données...")

    if not check_docker_installed():
        sys.exit(1)

    check_env_file()

    if not start_database():
        sys.exit(1)

    if not wait_for_database():
        sys.exit(1)

    if not setup_database():
        sys.exit(1)

    logger.info("""
Installation de la base de données terminée avec succès !

Pour utiliser la base de données :
1. Les conteneurs Docker sont maintenant en cours d'exécution
2. La base de données est accessible sur localhost:5432
3. Les identifiants par défaut sont dans le fichier .env
4. Les migrations ont été appliquées

Pour gérer les migrations :
- Créer une nouvelle migration : python manage_migrations.py create "description"
- Mettre à jour la base : python manage_migrations.py upgrade
- Voir l'état actuel : python manage_migrations.py current
- Voir l'historique : python manage_migrations.py history
""")

if __name__ == "__main__":
    main()
