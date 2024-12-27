"""
Classe principale pour la gestion des connexions à PostgreSQL.
Implémente le pattern Singleton pour assurer une seule instance de connexion.
"""

import os
from typing import Optional
from contextlib import contextmanager
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _engine = None
    _SessionLocal = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._initialize_engine()

    def _initialize_engine(self):
        """Initialise le moteur SQLAlchemy avec les paramètres de connexion."""
        try:
            db_params = self._get_connection_params()
            self._engine = create_engine(
                self._build_connection_string(db_params),
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_pre_ping=True,
                echo=False
            )
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            logger.info("Moteur de base de données initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du moteur de base de données: {e}")
            raise

    def _get_connection_params(self) -> dict:
        """Récupère les paramètres de connexion depuis les variables d'environnement."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'auditronai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }

    def _build_connection_string(self, params: dict) -> str:
        """Construit la chaîne de connexion PostgreSQL."""
        return (
            f"postgresql://{params['user']}:{params['password']}@"
            f"{params['host']}:{params['port']}/{params['database']}"
        )

    @contextmanager
    def get_session(self) -> Session:
        """
        Fournit un contexte de session de base de données.
        Gère automatiquement les transactions et les erreurs.
        
        Usage:
            with db.get_session() as session:
                session.query(User).all()
        """
        if not self._SessionLocal:
            raise RuntimeError("La base de données n'est pas initialisée")

        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erreur lors de la transaction: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur inattendue: {e}")
            raise
        finally:
            session.close()

    def get_engine(self):
        """Retourne le moteur SQLAlchemy."""
        return self._engine

    def dispose(self):
        """Libère toutes les connexions du pool."""
        if self._engine:
            self._engine.dispose()
            logger.info("Connexions à la base de données libérées")

    def health_check(self) -> bool:
        """Vérifie l'état de la connexion à la base de données."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Échec du contrôle de santé de la base de données: {e}")
            return False

    def __del__(self):
        """Assure la libération des ressources lors de la destruction de l'instance."""
        self.dispose()
