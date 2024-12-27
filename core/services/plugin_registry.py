"""Module de gestion du registre des plugins."""
from typing import Dict, Type, Any
from AuditronAI.core.services.analysis_plugins.base import AnalysisPlugin

class PluginRegistry:
    """Registre des plugins d'analyse."""
    
    _plugins: Dict[str, Type[AnalysisPlugin]] = {}
    
    @classmethod
    def register(cls, name: str, plugin_class: Type[AnalysisPlugin]) -> None:
        """
        Enregistre un nouveau plugin.
        
        Args:
            name: Nom unique du plugin
            plugin_class: Classe du plugin
        """
        if not issubclass(plugin_class, AnalysisPlugin):
            raise TypeError("Le plugin doit hériter de AnalysisPlugin")
            
        cls._plugins[name] = plugin_class
        
    @classmethod
    def get(cls, name: str) -> Type[AnalysisPlugin]:
        """
        Récupère un plugin par son nom.
        
        Args:
            name: Nom du plugin
            
        Returns:
            Classe du plugin
            
        Raises:
            KeyError: Si le plugin n'existe pas
        """
        if name not in cls._plugins:
            raise KeyError(f"Plugin '{name}' non trouvé")
            
        return cls._plugins[name]
        
    @classmethod
    def list_plugins(cls) -> Dict[str, Type[AnalysisPlugin]]:
        """
        Liste tous les plugins enregistrés.
        
        Returns:
            Dict des plugins enregistrés
        """
        return cls._plugins.copy()
        
    @classmethod
    def clear(cls) -> None:
        """Supprime tous les plugins enregistrés."""
        cls._plugins.clear()
