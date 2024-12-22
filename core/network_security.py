import os
from pathlib import Path
from typing import Dict, Any
import json
from .logger import logger

class NetworkSecurity:
    def __init__(self):
        """Initialise la configuration de sécurité réseau."""
        self.config = {
            'server_address': os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost'),
            'server_port': int(os.getenv('STREAMLIT_SERVER_PORT', 8501)),
            'headless': os.getenv('STREAMLIT_SERVER_HEADLESS', 'false').lower() == 'true',
            'enable_cors': True,
            'enable_xsrf': os.getenv('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', 'true').lower() == 'true',
            'external_access': os.getenv('STREAMLIT_EXTERNAL_ACCESS', 'false').lower() == 'true'
        }
        
        # Vérifier la configuration
        self._validate_config()
        
    def _validate_config(self):
        """Valide la configuration réseau."""
        if self.config['external_access']:
            logger.warning("⚠️ Accès externe activé - Non recommandé en production")
            
        if not self.config['enable_xsrf']:
            logger.warning("⚠️ Protection XSRF désactivée - Non recommandé")
            
        if self.config['server_address'] != 'localhost':
            logger.warning("⚠️ Serveur non restreint à localhost")
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour Streamlit."""
        return {
            'server.address': self.config['server_address'],
            'server.port': int(self.config['server_port']),
            'server.headless': bool(self.config['headless']),
            'server.enableCORS': True if self.config['enable_xsrf'] else bool(self.config['enable_cors']),
            'server.enableXsrfProtection': bool(self.config['enable_xsrf']),
            'browser.gatherUsageStats': 0
        }
    
    def write_streamlit_config(self):
        """Écrit la configuration dans .streamlit/config.toml."""
        config_dir = Path.home() / '.streamlit'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'config.toml'
        
        with open(config_file, 'w') as f:
            for key, value in self.get_streamlit_config().items():
                if isinstance(value, bool):
                    f.write(f'{key} = {str(value).lower()}\n')
                elif isinstance(value, (int, float)):
                    f.write(f'{key} = {value}\n')
                else:
                    f.write(f'{key} = "{value}"\n')
        
        logger.info("Configuration réseau sécurisée appliquée")
    
    def is_secure(self) -> bool:
        """Vérifie si la configuration est sécurisée."""
        return (
            self.config['server_address'] == 'localhost' and
            not self.config['external_access'] and
            self.config['enable_xsrf'] and
            not self.config['enable_cors']
        ) 