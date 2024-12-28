"""Gestionnaire de plugins."""

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from app.core.logging import get_logger

logger = get_logger(__name__)

class Plugin(ABC):
    """Classe de base pour les plugins."""
    
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    
    def __init__(self):
        """Initialise le plugin."""
        if not self.name:
            self.name = self.__class__.__name__
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialise le plugin."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Nettoie le plugin."""
        pass
    
    def enable(self) -> None:
        """Active le plugin."""
        self.enabled = True
        logger.info(f"Plugin {self.name} activé")
    
    def disable(self) -> None:
        """Désactive le plugin."""
        self.enabled = False
        logger.info(f"Plugin {self.name} désactivé")
    
    def is_enabled(self) -> bool:
        """Vérifie si le plugin est activé.
        
        Returns:
            True si activé
        """
        return self.enabled
    
    def get_info(self) -> Dict[str, Any]:
        """Récupère les informations du plugin.
        
        Returns:
            Informations du plugin
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled
        }

class PluginManager:
    """Gestionnaire de plugins."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dirs: List[Path] = []
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Enregistre un plugin.
        
        Args:
            plugin: Plugin à enregistrer
        """
        if plugin.name in self.plugins:
            logger.warning(f"Plugin {plugin.name} déjà enregistré")
            return
        
        try:
            # Initialise le plugin
            plugin.initialize()
            
            # Enregistre le plugin
            self.plugins[plugin.name] = plugin
            
            logger.info(
                f"Plugin {plugin.name} enregistré",
                extra={"version": plugin.version}
            )
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'enregistrement du plugin {plugin.name}",
                extra={"error": str(e)},
                exc_info=True
            )
    
    def unregister_plugin(self, name: str) -> None:
        """Désenregistre un plugin.
        
        Args:
            name: Nom du plugin
        """
        if name not in self.plugins:
            logger.warning(f"Plugin {name} non trouvé")
            return
        
        try:
            # Récupère le plugin
            plugin = self.plugins[name]
            
            # Nettoie le plugin
            plugin.cleanup()
            
            # Supprime le plugin
            del self.plugins[name]
            
            logger.info(f"Plugin {name} désenregistré")
            
        except Exception as e:
            logger.error(
                f"Erreur lors du désenregistrement du plugin {name}",
                extra={"error": str(e)},
                exc_info=True
            )
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Récupère un plugin.
        
        Args:
            name: Nom du plugin
            
        Returns:
            Plugin ou None
        """
        return self.plugins.get(name)
    
    def get_plugins(self) -> Dict[str, Plugin]:
        """Récupère tous les plugins.
        
        Returns:
            Dictionnaire des plugins
        """
        return self.plugins
    
    def get_enabled_plugins(self) -> Dict[str, Plugin]:
        """Récupère les plugins activés.
        
        Returns:
            Dictionnaire des plugins activés
        """
        return {
            name: plugin
            for name, plugin in self.plugins.items()
            if plugin.is_enabled()
        }
    
    def add_plugin_dir(self, directory: Path) -> None:
        """Ajoute un dossier de plugins.
        
        Args:
            directory: Dossier à ajouter
        """
        if not directory.exists():
            logger.warning(f"Dossier {directory} non trouvé")
            return
        
        if directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)
            logger.info(f"Dossier de plugins {directory} ajouté")
    
    def discover_plugins(self) -> None:
        """Découvre les plugins dans les dossiers."""
        for directory in self.plugin_dirs:
            try:
                # Ajoute le dossier au path
                import sys
                sys.path.insert(0, str(directory))
                
                # Parcourt les modules
                for _, name, _ in pkgutil.iter_modules([str(directory)]):
                    try:
                        # Importe le module
                        module = importlib.import_module(name)
                        
                        # Recherche les classes de plugin
                        for item in dir(module):
                            obj = getattr(module, item)
                            if (
                                inspect.isclass(obj)
                                and issubclass(obj, Plugin)
                                and obj != Plugin
                            ):
                                # Crée et enregistre le plugin
                                plugin = obj()
                                self.register_plugin(plugin)
                                
                    except Exception as e:
                        logger.error(
                            f"Erreur lors du chargement du module {name}",
                            extra={"error": str(e)},
                            exc_info=True
                        )
                
            except Exception as e:
                logger.error(
                    f"Erreur lors de la découverte des plugins dans {directory}",
                    extra={"error": str(e)},
                    exc_info=True
                )
            
            finally:
                # Restaure le path
                sys.path.pop(0)
    
    def cleanup(self) -> None:
        """Nettoie tous les plugins."""
        for name, plugin in self.plugins.items():
            try:
                plugin.cleanup()
                logger.info(f"Plugin {name} nettoyé")
            except Exception as e:
                logger.error(
                    f"Erreur lors du nettoyage du plugin {name}",
                    extra={"error": str(e)},
                    exc_info=True
                )

# Instance globale
plugin_manager = PluginManager() 