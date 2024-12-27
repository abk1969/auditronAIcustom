"""Module de base pour le système de plugins."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import importlib
import pkgutil
from pathlib import Path

class PluginType(str, Enum):
    """Types de plugins supportés."""
    ANALYZER = "analyzer"
    FORMATTER = "formatter"
    REPORTER = "reporter"
    SECURITY = "security"
    METRICS = "metrics"
    CUSTOM = "custom"

@dataclass
class PluginMetadata:
    """Métadonnées d'un plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    config_schema: Optional[Dict] = None

class PluginInterface(ABC):
    """Interface de base pour tous les plugins."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialise le plugin avec sa configuration."""
        pass
    
    @abstractmethod
    def execute(self, data: Any) -> Dict[str, Any]:
        """Exécute le plugin sur les données fournies."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Nettoie les ressources du plugin."""
        pass
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Retourne les métadonnées du plugin."""
        pass 