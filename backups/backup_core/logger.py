"""Configuration du logger."""
import logging
import sys
from typing import Any

# Configuration du logger
logger = logging.getLogger("auditronai")
logger.setLevel(logging.INFO)

# Handler pour la console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Ajouter le handler au logger
logger.addHandler(console_handler)

def get_logger(name: str) -> Any:
    """Récupère un logger configuré.
    
    Args:
        name: Nom du logger
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(f"auditronai.{name}")
