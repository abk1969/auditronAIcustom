"""Système de plugins avancé."""
from typing import Dict, Any, List, Type, Optional
import importlib.util
import inspect
from pathlib import Path
import yaml
from dataclasses import dataclass
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

@dataclass
class PluginMetadata:
    """Métadonnées d'un plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    settings: Dict[str, Any]

class PluginInterface:
    """Interface de base pour les plugins."""
    
    @property
    @classmethod
    def metadata(cls) -> PluginMetadata:
        """Retourne les métadonnées du plugin."""
        raise NotImplementedError
    
    async def initialize(self) -> bool:
        """Initialise le plugin."""
        return True
    
    async def execute(self, **kwargs) -> Any:
        """Exécute le plugin."""
        raise NotImplementedError
    
    async def cleanup(self):
        """Nettoie les ressources."""
        pass

class PluginManager:
    """Gestionnaire de plugins."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialise le gestionnaire de plugins.
        
        Args:
            plugins_dir: Répertoire des plugins
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Type[PluginInterface]] = {}
        self.instances: Dict[str, PluginInterface] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._load_plugins()
    
    def _load_plugins(self):
        """Charge les plugins disponibles."""
        if not self.plugins_dir.exists():
            logger.warning(f"Répertoire de plugins non trouvé: {self.plugins_dir}")
            return
            
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
                
            try:
                # Charger la configuration
                config_file = plugin_dir / "plugin.yaml"
                if not config_file.exists():
                    continue
                    
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                    
                # Charger le module
                module_path = plugin_dir / "plugin.py"
                if not module_path.exists():
                    continue
                    
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_dir.name}",
                    module_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Trouver la classe du plugin
                for item in dir(module):
                    obj = getattr(module, item)
                    if (inspect.isclass(obj) and 
                        issubclass(obj, PluginInterface) and 
                        obj != PluginInterface):
                        
                        self.plugins[config['name']] = obj
                        logger.info(f"Plugin chargé: {config['name']}")
                        break
                        
            except Exception as e:
                logger.error(f"Erreur lors du chargement du plugin {plugin_dir.name}: {e}")
    
    async def initialize_plugin(self, name: str) -> bool:
        """
        Initialise un plugin.
        
        Args:
            name: Nom du plugin
        """
        try:
            if name not in self.plugins:
                logger.error(f"Plugin non trouvé: {name}")
                return False
                
            plugin_class = self.plugins[name]
            instance = plugin_class()
            
            if await instance.initialize():
                self.instances[name] = instance
                logger.info(f"Plugin initialisé: {name}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du plugin {name}: {e}")
            return False
    
    @telemetry.trace_method("execute_plugin")
    async def execute_plugin(self, name: str, **kwargs) -> Optional[Any]:
        """
        Exécute un plugin.
        
        Args:
            name: Nom du plugin
            **kwargs: Arguments pour le plugin
        """
        try:
            if name not in self.instances:
                if not await self.initialize_plugin(name):
                    return None
                    
            instance = self.instances[name]
            return await instance.execute(**kwargs)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du plugin {name}: {e}")
            return None
    
    async def cleanup(self):
        """Nettoie tous les plugins."""
        for name, instance in self.instances.items():
            try:
                await instance.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du plugin {name}: {e}")
        
        self.instances.clear()
        self.executor.shutdown() 