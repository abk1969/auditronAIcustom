"""Système de journalisation pour AuditronAI."""
import os
import sys
import logging
import logging.handlers
import asyncio
from typing import Optional, Dict, Any, Union, Callable
from pathlib import Path
from datetime import datetime
import json
from functools import wraps, partial
import traceback

class JsonFormatter(logging.Formatter):
    """Formateur de logs en JSON."""

    def __init__(self, **kwargs):
        """Initialise le formateur."""
        super().__init__()
        self.default_fields = kwargs

    def format(self, record: logging.LogRecord) -> str:
        """
        Formate l'enregistrement en JSON.
        
        Args:
            record: Enregistrement à formater
            
        Returns:
            Chaîne JSON formatée
        """
        message = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Ajouter les champs par défaut
        message.update(self.default_fields)

        # Ajouter les champs supplémentaires du record
        if hasattr(record, 'extra_fields'):
            message.update(record.extra_fields)

        # Ajouter les informations d'exception si présentes
        if record.exc_info:
            message['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'stack_trace': traceback.format_exception(*record.exc_info)
            }

        return json.dumps(message)

class SecurityLogger(logging.Logger):
    """Logger personnalisé avec fonctionnalités de sécurité."""

    def __init__(self, name: str, level: int = logging.NOTSET):
        """Initialise le logger."""
        super().__init__(name, level)
        self.sensitive_fields = {'password', 'token', 'secret', 'key', 'auth'}

    def _sanitize_data(self, data: Any) -> Any:
        """
        Nettoie les données sensibles.
        
        Args:
            data: Données à nettoyer
            
        Returns:
            Données nettoyées
        """
        if isinstance(data, dict):
            return {
                k: '[REDACTED]' if any(s in k.lower() for s in self.sensitive_fields)
                else self._sanitize_data(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        return data

    def _log_with_extra(
        self,
        level: int,
        msg: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> None:
        """
        Journalise avec des champs supplémentaires.
        
        Args:
            level: Niveau de log
            msg: Message à journaliser
            extra_fields: Champs supplémentaires
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        """
        if extra_fields:
            sanitized_extra = self._sanitize_data(extra_fields)
            kwargs['extra'] = {
                'extra_fields': sanitized_extra
            }
        super().log(level, msg, *args, **kwargs)

    def security_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Journalise un événement de sécurité.
        
        Args:
            event_type: Type d'événement
            description: Description de l'événement
            severity: Niveau de sévérité
            extra_fields: Champs supplémentaires
        """
        fields = {
            'event_type': event_type,
            'security_severity': severity
        }
        if extra_fields:
            fields.update(extra_fields)
            
        level = getattr(logging, severity.upper(), logging.INFO)
        self._log_with_extra(level, description, fields)

def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    rotation: str = "midnight",
    backup_count: int = 30,
    json_format: bool = True
) -> logging.Logger:
    """
    Configure le système de journalisation.
    
    Args:
        log_dir: Répertoire des logs
        log_level: Niveau de log
        rotation: Politique de rotation
        backup_count: Nombre de backups à conserver
        json_format: Utiliser le format JSON
        
    Returns:
        Logger configuré
    """
    # Créer le répertoire de logs si nécessaire
    os.makedirs(log_dir, exist_ok=True)

    # Créer le logger
    logging.setLoggerClass(SecurityLogger)
    logger = logging.getLogger('auditronai')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Configurer le handler pour fichier
    log_file = os.path.join(log_dir, 'auditronai.log')
    if rotation == "midnight":
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when="midnight",
            interval=1,
            backupCount=backup_count
        )
    else:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=backup_count
        )

    # Configurer le handler pour console
    console_handler = logging.StreamHandler(sys.stdout)

    # Configurer les formateurs
    if json_format:
        formatter = JsonFormatter(
            application="AuditronAI",
            environment=os.getenv('ENVIRONMENT', 'development')
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_execution_time(
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO
) -> Callable:
    """
    Décorateur pour mesurer le temps d'exécution.
    
    Args:
        logger: Logger à utiliser (utilise le logger par défaut si non spécifié)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                log = logger or logging.getLogger('auditronai')
                log._log_with_extra(
                    level,
                    f"{func.__name__} executed successfully",
                    {
                        'execution_time': execution_time,
                        'function': func.__name__
                    }
                )
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                
                log = logger or logging.getLogger('auditronai')
                log._log_with_extra(
                    logging.ERROR if level <= logging.INFO else level,
                    f"Error in {func.__name__}: {str(e)}",
                    {
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                log = logger or logging.getLogger('auditronai')
                log._log_with_extra(
                    level,
                    f"{func.__name__} executed successfully",
                    {
                        'execution_time': execution_time,
                        'function': func.__name__
                    }
                )
                return result
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                
                log = logger or logging.getLogger('auditronai')
                log._log_with_extra(
                    logging.ERROR if level <= logging.INFO else level,
                    f"Error in {func.__name__}: {str(e)}",
                    {
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Configurer le logger par défaut
logger = setup_logging()
