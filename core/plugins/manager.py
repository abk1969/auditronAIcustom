"""Gestionnaire de plugins."""
import logging
from typing import Dict, Type, List, Optional
from pathlib import Path
import yaml
import importlib.util
from .base import PluginInterface, PluginType, PluginMetadata

logger = logging.getLogger(__name__)

class PluginManager:
    """Gère le chargement et l'exécution des plugins."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialise le gestionnaire de plugins.
        
        Args:
            plugins_dir: Répertoire contenant les plugins
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Type[PluginInterface]] = {}
        self.instances: Dict[str, PluginInterface] = {}
        self.configs: Dict[str, Dict] = {}
        
    def discover_plugins(self) -> None:
        """Découvre et charge les plugins disponibles."""
        if not self.plugins_dir.exists():
            logger.warning(f"Répertoire de plugins non trouvé: {self.plugins_dir}")
            return
            
        for plugin_path in self.plugins_dir.glob("*/plugin.py"):
            try:
                # Charger le module
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_path.parent.name}",
                    plugin_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Charger la configuration
                config_path = plugin_path.parent / "config.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        self.configs[plugin_path.parent.name] = yaml.safe_load(f)
                
                # Enregistrer le plugin
                if hasattr(module, "Plugin"):
                    self.plugins[plugin_path.parent.name] = module.Plugin
                    logger.info(f"Plugin chargé: {plugin_path.parent.name}")
                    
            except Exception as e:
                logger.error(f"Erreur lors du chargement du plugin {plugin_path}: {e}")
                
    def initialize_plugin(self, name: str) -> Optional[PluginInterface]:
        """
        Initialise un plugin spécifique.
        
        Args:
            name: Nom du plugin à initialiser
            
        Returns:
            Instance du plugin ou None si erreur
        """
        if name not in self.plugins:
            logger.error(f"Plugin non trouvé: {name}")
            return None
            
        try:
            plugin_class = self.plugins[name]
            config = self.configs.get(name, {})
            instance = plugin_class()
            instance.initialize(config)
            self.instances[name] = instance
            return instance
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du plugin {name}: {e}")
            return None
            
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginMetadata]:
        """
        Retourne les plugins d'un type spécifique.
        
        Args:
            plugin_type: Type de plugins à retourner
            
        Returns:
            Liste des métadonnées des plugins du type spécifié
        """
        return [
            instance.metadata
            for instance in self.instances.values()
            if instance.metadata.plugin_type == plugin_type
        ]
        
    def execute_plugin(self, name: str, data: Any) -> Optional[Dict[str, Any]]:
        """
        Exécute un plugin spécifique.
        
        Args:
            name: Nom du plugin à exécuter
            data: Données à traiter
            
        Returns:
            Résultats du plugin ou None si erreur
        """
        if name not in self.instances:
            if not self.initialize_plugin(name):
                return None
                
        try:
            return self.instances[name].execute(data)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du plugin {name}: {e}")
            return None
            
    def cleanup(self) -> None:
        """Nettoie tous les plugins."""
        for name, instance in self.instances.items():
            try:
                instance.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du plugin {name}: {e}") 