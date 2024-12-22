from loguru import logger
from pathlib import Path
import sys
import os
from pythonjsonlogger import jsonlogger
import logging

def setup_logger():
    """Configure le système de logging."""
    # Créer le dossier de logs s'il n'existe pas
    log_file = os.getenv('LOG_FILE', 'logs/auditron.log')
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configuration loguru
    logger.remove()  # Supprimer le handler par défaut
    
    # Format selon la configuration
    if os.getenv('LOG_FORMAT', 'json') == 'json':
        # Logger JSON pour une meilleure intégration
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        log_handler.setFormatter(formatter)
        logger.add(log_handler)
    else:
        # Format texte standard
        logger.add(sys.stdout, format="{time} {level} {message}")
    
    # Ajouter le fichier de log
    logger.add(
        log_file,
        rotation="500 MB",
        retention="10 days",
        level=os.getenv('LOG_LEVEL', 'INFO')
    )
    
    return logger 