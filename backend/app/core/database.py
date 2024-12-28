"""Gestionnaire de base de données."""

from contextlib import contextmanager
from typing import Any, Generator, Optional
import asyncio
import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError

from app.core.base import Base
from app.core.config import settings
from app.core.monitoring import monitoring

logger = logging.getLogger(__name__)

__all__ = ['DatabaseManager', 'db', 'get_db']

class DatabaseManager:
    """Gestionnaire de base de données."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self._engine = None
        self._session_factory = None
        self._initialized = False
        
    @property
    def engine(self):
        """Récupère le moteur SQLAlchemy."""
        if not self._initialized:
            raise RuntimeError("La base de données n'est pas initialisée")
        return self._engine
        
    @property
    def SessionLocal(self):
        """Récupère le factory de session."""
        if not self._initialized:
            raise RuntimeError("La base de données n'est pas initialisée")
        return self._session_factory
        
    def _create_engine(self):
        """Crée le moteur SQLAlchemy."""
        if not settings.SQLALCHEMY_DATABASE_URI:
            raise ValueError("L'URL de la base de données n'est pas configurée")
            
        return create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=settings.DEBUG
        )
        
    async def init_db(self, max_retries: int = 10, retry_interval: int = 10) -> None:
        """Initialise la connexion à la base de données avec retry.
        
        Args:
            max_retries: Nombre maximum de tentatives
            retry_interval: Intervalle entre les tentatives en secondes
        """
        if self._initialized:
            return
            
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentative de connexion à la base de données {attempt + 1}/{max_retries}")
                
                # Crée le moteur
                self._engine = self._create_engine()
                
                # Vérifie la connexion
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                # Configure les événements
                event.listen(self._engine, "before_cursor_execute", self._before_cursor_execute)
                event.listen(self._engine, "after_cursor_execute", self._after_cursor_execute)
                
                # Crée le sessionmaker
                self._session_factory = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
                
                self._initialized = True
                logger.info("Connexion à la base de données établie avec succès")
                return
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        "Impossible de se connecter à la base de données après plusieurs tentatives",
                        extra={"error": str(e)},
                        exc_info=True
                    )
                    raise
                
                logger.warning(
                    f"Tentative de connexion {attempt + 1}/{max_retries} échouée, nouvelle tentative dans {retry_interval}s",
                    extra={"error": str(e)}
                )
                await asyncio.sleep(retry_interval)
    
    async def check_health(self) -> bool:
        """Vérifie l'état de santé de la base de données.
        
        Returns:
            True si la base de données est en bonne santé
        """
        try:
            if not self._initialized:
                return False
                
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.error(
                "Erreur lors de la vérification de santé de la base de données",
                extra={"error": str(e)},
                exc_info=True
            )
            return False
        
    def _before_cursor_execute(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool
    ) -> None:
        """Événement avant l'exécution d'une requête."""
        context._query_start_time = monitoring.get_time()
        
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
        """Événement après l'exécution d'une requête."""
        total_time = monitoring.get_time() - context._query_start_time
        operation = statement.split()[0].lower()
        
        monitoring.track_database_query(
            operation=operation,
            table="unknown",
            duration=total_time
        )
        
        if settings.DEBUG:
            logger.debug(
                "Requête SQL terminée",
                extra={
                    "duration": total_time,
                    "operation": operation
                }
            )
    
    def get_session(self) -> Session:
        """Récupère une session."""
        if not self._initialized:
            raise RuntimeError("La base de données n'est pas initialisée")
        return self._session_factory()
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Gestionnaire de contexte pour les sessions."""
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
        if self._engine:
            self._engine.dispose()
            self._initialized = False

# Instance globale
db = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI pour les sessions."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()