"""Gestionnaire de base de données."""

from contextlib import contextmanager
from typing import Any, Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import monitoring

logger = get_logger(__name__)

class DatabaseManager:
    """Gestionnaire de base de données."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=settings.DEBUG
        )
        
        # Configure les événements
        event.listen(self.engine, "before_cursor_execute", self._before_cursor_execute)
        event.listen(self.engine, "after_cursor_execute", self._after_cursor_execute)
        
        # Crée le sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def _before_cursor_execute(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool
    ) -> None:
        """Événement avant l'exécution d'une requête.
        
        Args:
            conn: Connexion
            cursor: Curseur
            statement: Requête SQL
            parameters: Paramètres
            context: Contexte
            executemany: Exécution multiple
        """
        # Stocke le temps de début
        context._query_start_time = monitoring.get_time()
        
        # Log la requête en mode debug
        if settings.DEBUG:
            logger.debug(
                "Exécution de requête SQL",
                extra={
                    "statement": statement,
                    "parameters": parameters
                }
            )
    
    def _after_cursor_execute(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool
    ) -> None:
        """Événement après l'exécution d'une requête.
        
        Args:
            conn: Connexion
            cursor: Curseur
            statement: Requête SQL
            parameters: Paramètres
            context: Contexte
            executemany: Exécution multiple
        """
        # Calcule la durée
        total_time = monitoring.get_time() - context._query_start_time
        
        # Détermine l'opération
        operation = statement.split()[0].lower()
        
        # Met à jour les métriques
        monitoring.track_database_query(
            operation=operation,
            table="unknown",  # TODO: Extraire la table
            duration=total_time
        )
        
        # Log la durée en mode debug
        if settings.DEBUG:
            logger.debug(
                "Requête SQL terminée",
                extra={
                    "duration": total_time,
                    "operation": operation
                }
            )
    
    def get_session(self) -> Session:
        """Récupère une session.
        
        Returns:
            Session de base de données
        """
        return self.SessionLocal()
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Gestionnaire de contexte pour les sessions.
        
        Yields:
            Session de base de données
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(
                "Erreur lors de la transaction",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
        finally:
            session.close()
    
    def dispose(self) -> None:
        """Libère les ressources."""
        self.engine.dispose()

# Instance globale
db = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI pour les sessions.
    
    Yields:
        Session de base de données
    """
    session = db.get_session()
    try:
        yield session
    finally:
        session.close() 