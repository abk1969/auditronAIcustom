"""
Gestion des sessions de base de données.
Fournit des utilitaires pour initialiser la base de données et obtenir des sessions.
"""

from contextlib import contextmanager
from typing import Generator
import logging

from sqlalchemy.orm import Session

from .database import Database
from .models import Base

logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialise la base de données en créant toutes les tables définies dans les modèles.
    Cette fonction doit être appelée au démarrage de l'application.
    """
    try:
        db = Database()
        Base.metadata.create_all(bind=db.get_engine())
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Fournit un contexte de session de base de données.
    À utiliser dans les applications Streamlit pour les opérations de base de données.

    Usage:
        with get_db_session() as session:
            results = session.query(User).all()
    
    Yields:
        Session: Une session SQLAlchemy active
    """
    db = Database()
    with db.get_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Erreur lors de l'utilisation de la session: {e}")
            raise

def get_db() -> Database:
    """
    Retourne l'instance unique de la base de données.
    Utile pour les cas où l'accès direct à l'objet Database est nécessaire.

    Returns:
        Database: L'instance unique de la base de données
    """
    return Database()

def check_db_connection() -> bool:
    """
    Vérifie si la connexion à la base de données est active.
    Utile pour les contrôles de santé de l'application.

    Returns:
        bool: True si la connexion est active, False sinon
    """
    try:
        db = Database()
        return db.health_check()
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la connexion: {e}")
        return False
