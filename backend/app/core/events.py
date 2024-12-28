"""Gestionnaires d'événements de l'application."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from fastapi import FastAPI
from alembic.config import Config
from alembic import command

from app.core.config import settings
from app.core.database import db
from app.core.base import Base

logger = logging.getLogger(__name__)

async def run_migrations():
    """Exécute les migrations de manière asynchrone."""
    def _run_migrations():
        try:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Migrations exécutées avec succès")
        except Exception as e:
            logger.error(
                "Erreur lors de l'exécution des migrations",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    # Exécute les migrations dans un thread séparé
    with ThreadPoolExecutor() as executor:
        await asyncio.get_event_loop().run_in_executor(executor, _run_migrations)

async def initialize_database():
    """Initialise la base de données."""
    try:
        logger.info("Initialisation de la base de données...")
        await db.init_db()
        
        # Attend que la base de données soit prête
        for attempt in range(5):  # 5 tentatives maximum
            if await db.check_health():
                logger.info("Base de données prête !")
                break
            logger.warning(f"La base de données n'est pas prête (tentative {attempt + 1}/5)")
            await asyncio.sleep(2)
        else:
            raise RuntimeError("La base de données n'est pas prête après plusieurs tentatives")
            
        # Exécute les migrations
        logger.info("Exécution des migrations...")
        await run_migrations()
        
        # Crée les tables si elles n'existent pas
        def create_tables():
            logger.info("Création des tables...")
            Base.metadata.create_all(bind=db.engine)
            logger.info("Tables créées avec succès")
            
        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(executor, create_tables)
            
    except Exception as e:
        logger.error(
            "Erreur lors de l'initialisation de la base de données",
            extra={"error": str(e)},
            exc_info=True
        )
        raise

def create_start_app_handler(app: FastAPI) -> Callable:
    """Crée le gestionnaire de démarrage de l'application.
    
    Args:
        app: Application FastAPI
        
    Returns:
        Fonction de démarrage
    """
    async def start_app() -> None:
        """Démarre l'application."""
        try:
            logger.info("Démarrage de l'application...")
            
            # Initialise la base de données
            await initialize_database()
            
            # Crée les dossiers nécessaires
            for directory in [settings.LOG_DIR, settings.UPLOAD_DIR]:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Dossier créé : {directory}")
            
            if settings.PROMETHEUS_MULTIPROC_DIR:
                settings.PROMETHEUS_MULTIPROC_DIR.mkdir(parents=True, exist_ok=True)
                logger.info(f"Dossier Prometheus créé : {settings.PROMETHEUS_MULTIPROC_DIR}")
            
            logger.info("Application démarrée avec succès")
            
        except Exception as e:
            logger.error(
                "Erreur lors du démarrage de l'application",
                extra={"error": str(e)},
                exc_info=True
            )
            raise

    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """Crée le gestionnaire d'arrêt de l'application.
    
    Args:
        app: Application FastAPI
        
    Returns:
        Fonction d'arrêt
    """
    async def stop_app() -> None:
        """Arrête l'application."""
        try:
            logger.info("Arrêt de l'application...")
            
            # Libère les ressources de la base de données
            db.dispose()
            logger.info("Ressources de la base de données libérées")
            
            logger.info("Application arrêtée avec succès")
            
        except Exception as e:
            logger.error(
                "Erreur lors de l'arrêt de l'application",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    return stop_app