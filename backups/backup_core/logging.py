"""Gestionnaire de journalisation."""

import json
import logging
import logging.config
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings

class JsonFormatter(logging.Formatter):
    """Formateur de logs JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formate un enregistrement de log en JSON.
        
        Args:
            record: Enregistrement à formater
            
        Returns:
            Log formaté
        """
        # Données de base
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Ajoute les données supplémentaires
        if hasattr(record, "data"):
            log_data["data"] = record.data
        
        # Ajoute les informations d'exception
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Ajoute les données extra
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure la journalisation."""
    # Crée le dossier de logs
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration de base
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(log_dir / "app.log"),
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": str(log_dir / "error.log"),
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5,
                "level": "ERROR"
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": settings.LOG_LEVEL,
                "propagate": True
            },
            "app": {  # Application logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "uvicorn": {  # Uvicorn logger
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    
    # Configure le logging
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Récupère un logger.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """Adaptateur de logger avec contexte."""
    
    def __init__(
        self,
        logger: logging.Logger,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'adaptateur.
        
        Args:
            logger: Logger à adapter
            extra: Données supplémentaires
        """
        super().__init__(logger, extra or {})
    
    def process(
        self,
        msg: str,
        kwargs: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Traite un message de log.
        
        Args:
            msg: Message
            kwargs: Arguments
            
        Returns:
            Message et arguments traités
        """
        # Ajoute les données extra
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs

class ContextLogger:
    """Logger avec contexte."""
    
    def __init__(self, name: str):
        """Initialise le logger.
        
        Args:
            name: Nom du logger
        """
        self.logger = get_logger(name)
        self.context: Dict[str, Any] = {}
    
    def add_context(self, **kwargs: Any) -> None:
        """Ajoute du contexte.
        
        Args:
            **kwargs: Données de contexte
        """
        self.context.update(kwargs)
    
    def remove_context(self, *keys: str) -> None:
        """Supprime du contexte.
        
        Args:
            *keys: Clés à supprimer
        """
        for key in keys:
            self.context.pop(key, None)
    
    def clear_context(self) -> None:
        """Vide le contexte."""
        self.context.clear()
    
    def get_logger(self) -> logging.Logger:
        """Récupère le logger avec contexte.
        
        Returns:
            Logger avec contexte
        """
        return LoggerAdapter(self.logger, self.context)

# Configure le logging au démarrage
setup_logging() 