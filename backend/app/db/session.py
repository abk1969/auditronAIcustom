"""Gestionnaire de base de données."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import monitoring

logger = get_logger(__name__)

# Création du moteur SQLAlchemy
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False
)

# Création du SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """Récupère une session de base de données.
    
    Yields:
        Session de base de données
    """
    db = SessionLocal()
    try:
        monitoring.db_connections_in_use.inc()
        yield db
    finally:
        monitoring.db_connections_in_use.dec()
        db.close()

@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager pour une session de base de données.
    
    Yields:
        Session de base de données
    """
    db = SessionLocal()
    try:
        monitoring.db_connections_in_use.inc()
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            "Erreur lors de la transaction",
            extra={"error": str(e)}
        )
        raise
    finally:
        monitoring.db_connections_in_use.dec()
        db.close()

def init_db() -> None:
    """Initialise la base de données."""
    try:
        # Import des modèles pour créer les tables
        from app.models import base
        
        logger.info("Création des tables...")
        base.Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès")
        
    except Exception as e:
        logger.error(
            "Erreur lors de l'initialisation de la base de données",
            extra={"error": str(e)}
        )
        raise 