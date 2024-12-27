"""Système de configuration modulaire."""
from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from dataclasses import dataclass
from ..logger import logger

@dataclass
class ModuleConfig:
    """Configuration d'un module."""
    name: str
    enabled: bool
    settings: Dict[str, Any]
    dependencies: Dict[str, str]

class ConfigurationManager:
    """Gestionnaire de configuration modulaire."""
    
    def __init__(self, config_dir: str = "configs"):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_dir: Répertoire des fichiers de configuration
        """
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, ModuleConfig] = {}
        self.env_overrides: Dict[str, Dict[str, Any]] = {}
        
        # Charger les configurations
        self._load_configs()
        self._apply_env_overrides()
    
    def _load_configs(self):
        """Charge les configurations des modules."""
        if not self.config_dir.exists():
            logger.warning(f"Répertoire de configuration non trouvé: {self.config_dir}")
            return
            
        for config_file in self.config_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    
                module_name = config_file.stem
                self.configs[module_name] = ModuleConfig(
                    name=module_name,
                    enabled=config_data.get('enabled', True),
                    settings=config_data.get('settings', {}),
                    dependencies=config_data.get('dependencies', {})
                )
                logger.info(f"Configuration chargée pour {module_name}")
                
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {config_file}: {e}")
    
    def _apply_env_overrides(self):
        """Applique les surcharges d'environnement."""
        import os
        
        for key, value in os.environ.items():
            if key.startswith('AUDITRONAI_'):
                parts = key.lower().split('_')[1:]  # Enlever le préfixe
                if len(parts) >= 2:
                    module = parts[0]
                    setting = '_'.join(parts[1:])
                    
                    if module not in self.env_overrides:
                        self.env_overrides[module] = {}
                    
                    # Convertir la valeur selon le type
                    try:
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '').isdigit():
                            value = float(value)
                    except:
                        pass
                        
                    self.env_overrides[module][setting] = value
    
    def get_config(self, module: str) -> Optional[ModuleConfig]:
        """Récupère la configuration d'un module."""
        try:
            if module not in self.configs:
                logger.error(f"Module non trouvé: {module}")
                return None
                
            config = self.configs[module]
            
            # Appliquer les surcharges
            if module in self.env_overrides:
                config.settings.update(self.env_overrides[module])
                
            return config
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la configuration: {e}")
            return None 