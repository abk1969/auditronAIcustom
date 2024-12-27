"""Registre des analyseurs disponibles."""
from typing import Dict, Type

from .interfaces import AnalyzerType
from .base_analyzer import BaseAnalyzer
from .script_analyzer import ScriptAnalyzer
from .vulture_analyzer import VultureAnalyzer
from .prospector_analyzer import ProspectorAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .sql_analyzer import SQLAnalyzer
from .radon_analyzer import RadonAnalyzer
from .bandit_analyzer import BanditAnalyzer

class AnalyzerRegistration:
    """Registre central des analyseurs disponibles."""
    
    _instance = None

    def __init__(self):
        """Initialise le registre avec les analyseurs par défaut."""
        self._analyzers: Dict[AnalyzerType, Type[BaseAnalyzer]] = {
            AnalyzerType.SCRIPT: ScriptAnalyzer,
            AnalyzerType.UNUSED: VultureAnalyzer,
            AnalyzerType.QUALITY: ProspectorAnalyzer,
            AnalyzerType.TYPESCRIPT: TypeScriptAnalyzer,
            AnalyzerType.SQL: SQLAnalyzer,
            AnalyzerType.COMPLEXITY: RadonAnalyzer,
            AnalyzerType.SECURITY: BanditAnalyzer
        }

    def register(self, analyzer_type: AnalyzerType, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        Enregistre un nouvel analyseur.
        
        Args:
            analyzer_type: Type d'analyseur
            analyzer_class: Classe d'analyseur
        """
        if not issubclass(analyzer_class, BaseAnalyzer):
            raise ValueError("L'analyseur doit hériter de BaseAnalyzer")
            
        self._analyzers[analyzer_type] = analyzer_class

    def unregister(self, analyzer_type: AnalyzerType) -> None:
        """
        Supprime un analyseur du registre.
        
        Args:
            analyzer_type: Type d'analyseur à supprimer
        """
        if analyzer_type in self._analyzers:
            del self._analyzers[analyzer_type]

    def get_analyzer(self, analyzer_type: AnalyzerType) -> Type[BaseAnalyzer]:
        """
        Récupère un analyseur par son type.
        
        Args:
            analyzer_type: Type d'analyseur
            
        Returns:
            Classe d'analyseur correspondante
            
        Raises:
            KeyError: Si l'analyseur n'existe pas
        """
        if analyzer_type not in self._analyzers:
            raise KeyError(f"Analyseur non trouvé: {analyzer_type}")
            
        return self._analyzers[analyzer_type]

    def get_all_analyzers(self) -> Dict[AnalyzerType, Type[BaseAnalyzer]]:
        """
        Récupère tous les analyseurs enregistrés.
        
        Returns:
            Dict des analyseurs par type
        """
        return self._analyzers.copy()

    def clear(self) -> None:
        """Supprime tous les analyseurs du registre."""
        self._analyzers.clear()

    @classmethod
    def get_instance(cls) -> 'AnalyzerRegistration':
        """
        Récupère l'instance unique du registre (pattern Singleton).
        
        Returns:
            Instance unique du registre
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_available_analyzers(cls) -> Dict[str, str]:
        """
        Récupère la liste des analyseurs disponibles avec leurs descriptions.
        
        Returns:
            Dict avec les types d'analyseurs et leurs descriptions
        """
        instance = cls.get_instance()
        return {str(k): v.__doc__ or "" for k, v in instance._analyzers.items()}

    @classmethod
    def register_analyzer(cls, analyzer_type: AnalyzerType, analyzer_class: Type[BaseAnalyzer]) -> None:
        """
        Enregistre un nouvel analyseur.
        
        Args:
            analyzer_type: Type d'analyseur
            analyzer_class: Classe d'analyseur
        """
        instance = cls.get_instance()
        instance.register(analyzer_type, analyzer_class)

# Instance globale du registre
default_registry = AnalyzerRegistration.get_instance()

def initialize_analyzers() -> None:
    """Initialise le système d'analyseurs avec les configurations par défaut."""
    # Cette fonction est appelée au chargement du module pour configurer
    # les analyseurs avec leurs paramètres par défaut
    pass
