"""
AuditronAI.core.config_manager
---------------------------
Gestion centralisée de la configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from .logger import logger

class ConfigManager:
    """Gère la configuration centralisée de l'application."""
    
    def __init__(self):
        """Initialise le gestionnaire de configuration."""
        self.env_path = Path(".env")
        load_dotenv(self.env_path)
        
        # Configuration par défaut
        self.defaults = {
            'AI_SERVICE': 'google',
            'OPENAI_MODEL': 'gpt-4o-mini',
            'GOOGLE_MODEL': 'gemini-2.0-flash-exp',
            'TEMPERATURE': '0.7',
            'MAX_TOKENS': '2000',
            'MAX_FILE_SIZE': '500000',
            'SECURITY_TIMEOUT': '30',
            'SECURITY_MAX_ISSUES': '100',
            'SECURITY_MIN_CONFIDENCE': '0.8'
        }
        
        # Appliquer les valeurs par défaut si nécessaire
        self._apply_defaults()
    
    def _apply_defaults(self):
        """Applique les valeurs par défaut manquantes."""
        for key, value in self.defaults.items():
            if not os.getenv(key):
                try:
                    set_key(self.env_path, key, value)
                    logger.info(f"Valeur par défaut appliquée pour {key}")
                except Exception as e:
                    logger.warning(f"Impossible d'appliquer la valeur par défaut pour {key}: {str(e)}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration complète.
        
        Returns:
            Dict[str, Any]: Configuration complète de l'application
        """
        try:
            return {
                'ai': {
                    'service': os.getenv('AI_SERVICE'),
                    'openai_model': os.getenv('OPENAI_MODEL'),
                    'google_model': os.getenv('GOOGLE_MODEL'),
                    'temperature': float(os.getenv('TEMPERATURE', 0.7)),
                    'max_tokens': int(os.getenv('MAX_TOKENS', 2000))
                },
                'security': {
                    'timeout': int(os.getenv('SECURITY_TIMEOUT', 30)),
                    'max_issues': int(os.getenv('SECURITY_MAX_ISSUES', 100)),
                    'min_confidence': float(os.getenv('SECURITY_MIN_CONFIDENCE', 0.8))
                },
                'analysis': {
                    'max_file_size': int(os.getenv('MAX_FILE_SIZE', 500000)),
                    'exclude_patterns': os.getenv('EXCLUDE_PATTERNS', '').split(',')
                }
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Erreur lors de la lecture de la configuration: {str(e)}")
            raise ValueError(f"Configuration invalide: {str(e)}")
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Met à jour la configuration.
        
        Args:
            updates: Dictionnaire des mises à jour à appliquer
            
        Raises:
            ValueError: Si une valeur est invalide
        """
        try:
            for key, value in updates.items():
                set_key(self.env_path, key, str(value))
            load_dotenv(override=True)
            logger.info("Configuration mise à jour avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration: {str(e)}")
            raise