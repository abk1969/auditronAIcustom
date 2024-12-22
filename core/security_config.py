"""
AuditronAI.core.security_config
----------------------------
Configuration de sécurité et validation.
"""

from typing import Dict, Any
from pathlib import Path
import json
from .logger import logger

class SecurityConfig:
    def __init__(self):
        """Initialise la configuration de sécurité."""
        self.config_file = Path('data/security_config.json')
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuration par défaut
        self.default_config = {
            'thresholds': {
                'critical': 0,
                'high': 2,
                'medium': 5
            },
            'checks': [
                "sql-injection",
                "xss",
                "code-injection",
                "command-injection",
                "path-traversal",
                "crypto-weak",
                "secrets-exposure",
                "auth-bypass",
                "unsafe-deserialization",
                "insecure-transport"
            ],
            'ignore_patterns': [
                "test_*.py",
                "*_test.py"
            ]
        }
        
        # Charger ou créer la configuration
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Configuration corrompue, utilisation des valeurs par défaut")
                self.config = self.default_config
        else:
            self.config = self.default_config
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration de sécurité sauvegardée")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
            raise 