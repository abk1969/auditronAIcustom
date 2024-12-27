"""Module contenant la classe de base pour les plugins d'analyse."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class AnalysisPlugin(ABC):
    """Classe abstraite pour les plugins d'analyse."""
    
    @abstractmethod
    def analyze(self, code: str, filename: str) -> Dict[str, Any]:
        """Effectue l'analyse selon le plugin."""
        pass
