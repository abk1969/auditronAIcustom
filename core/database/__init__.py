"""
Module de gestion de la base de données PostgreSQL.
Fournit une interface unifiée pour la connexion et les opérations sur la base de données.
"""

from .database import Database
from .models import Base
from .session import get_db_session, init_db

__all__ = ['Database', 'Base', 'get_db_session', 'init_db']
