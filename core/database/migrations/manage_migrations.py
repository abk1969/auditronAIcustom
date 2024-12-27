"""
Script de gestion des migrations de base de données.
Fournit des commandes pour créer et appliquer les migrations Alembic.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_alembic_config():
    """Retourne la configuration Alembic."""
    current_dir = Path(__file__).parent
    alembic_ini = current_dir.parent / "alembic.ini"
    
    if not alembic_ini.exists():
        raise FileNotFoundError(f"Le fichier alembic.ini n'a pas été trouvé à {alembic_ini}")
    
    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(current_dir))
    return config

def create_migration(message: str):
    """
    Crée un nouveau fichier de migration.
    
    Args:
        message: Description de la migration
    """
    try:
        config = get_alembic_config()
        command.revision(config, message=message, autogenerate=True)
        logger.info(f"Migration créée avec succès: {message}")
    except CommandError as e:
        logger.error(f"Erreur lors de la création de la migration: {e}")
        sys.exit(1)

def upgrade_database(revision: str = "head"):
    """
    Met à jour la base de données vers la dernière version ou une version spécifique.
    
    Args:
        revision: Version cible (par défaut: "head" pour la dernière version)
    """
    try:
        config = get_alembic_config()
        command.upgrade(config, revision)
        logger.info(f"Base de données mise à jour vers la version: {revision}")
    except CommandError as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {e}")
        sys.exit(1)

def downgrade_database(revision: str):
    """
    Rétrograde la base de données vers une version antérieure.
    
    Args:
        revision: Version cible ou nombre de versions à reculer (ex: "-1")
    """
    try:
        config = get_alembic_config()
        command.downgrade(config, revision)
        logger.info(f"Base de données rétrogradée vers la version: {revision}")
    except CommandError as e:
        logger.error(f"Erreur lors de la rétrogradation de la base de données: {e}")
        sys.exit(1)

def show_history():
    """Affiche l'historique des migrations."""
    try:
        config = get_alembic_config()
        command.history(config)
    except CommandError as e:
        logger.error(f"Erreur lors de l'affichage de l'historique: {e}")
        sys.exit(1)

def show_current():
    """Affiche la version actuelle de la base de données."""
    try:
        config = get_alembic_config()
        command.current(config)
    except CommandError as e:
        logger.error(f"Erreur lors de l'affichage de la version actuelle: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Gestionnaire de migrations de base de données")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande create
    create_parser = subparsers.add_parser("create", help="Crée une nouvelle migration")
    create_parser.add_argument("message", help="Description de la migration")

    # Commande upgrade
    upgrade_parser = subparsers.add_parser("upgrade", help="Met à jour la base de données")
    upgrade_parser.add_argument("--revision", default="head", help="Version cible (défaut: head)")

    # Commande downgrade
    downgrade_parser = subparsers.add_parser("downgrade", help="Rétrograde la base de données")
    downgrade_parser.add_argument("revision", help="Version cible ou nombre de versions (-1, -2, etc.)")

    # Autres commandes
    subparsers.add_parser("history", help="Affiche l'historique des migrations")
    subparsers.add_parser("current", help="Affiche la version actuelle")

    args = parser.parse_args()

    if args.command == "create":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_database(args.revision)
    elif args.command == "downgrade":
        downgrade_database(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
