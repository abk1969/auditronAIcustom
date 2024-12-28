"""Scripts de gestion de la base de données."""

import os
import sys
from pathlib import Path

# Ajoute le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command

def create_migration(message: str) -> None:
    """Crée une nouvelle migration.
    
    Args:
        message: Message de la migration
    """
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)

def upgrade_db() -> None:
    """Met à jour la base de données."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def downgrade_db() -> None:
    """Annule la dernière migration."""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db.py [create|upgrade|downgrade] [message]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "create":
        if len(sys.argv) < 3:
            print("Usage: python db.py create <message>")
            sys.exit(1)
        create_migration(sys.argv[2])
    elif action == "upgrade":
        upgrade_db()
    elif action == "downgrade":
        downgrade_db()
    else:
        print(f"Action inconnue: {action}")
        sys.exit(1) 