"""Package des analyseurs de code."""
from typing import Dict, Any, Type

from .interfaces import (
    Analyzer,
    AnalyzerType,
    AnalyzerContext
)
from .factory import AnalyzerFactory
from .base_analyzer import BaseAnalyzer
from .bandit_analyzer import BanditAnalyzer
from .radon_analyzer import RadonAnalyzer
from .vulture_analyzer import VultureAnalyzer
from .prospector_analyzer import ProspectorAnalyzer
from .script_analyzer import ScriptAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .registry import AnalyzerRegistration, initialize_analyzers

__all__ = [
    # Interfaces
    'Analyzer',
    'AnalyzerType',
    'AnalyzerContext',
    
    # Factory
    'AnalyzerFactory',
    
    # Base
    'BaseAnalyzer',
    
    # Analyseurs spécifiques
    'BanditAnalyzer',
    'RadonAnalyzer',
    'VultureAnalyzer',
    'ProspectorAnalyzer',
    'ScriptAnalyzer',
    'TypeScriptAnalyzer',
    
    # Registre
    'AnalyzerRegistration',
    'initialize_analyzers',
    
    # Fonctions utilitaires
    'get_analyzer_instance',
    'get_available_analyzers',
    'register_custom_analyzer'
]

def get_analyzer_instance(analyzer_type: AnalyzerType) -> Analyzer:
    """
    Crée une instance d'un analyseur spécifique.
    
    Args:
        analyzer_type: Type d'analyseur à créer
        
    Returns:
        Instance de l'analyseur
        
    Raises:
        ValueError: Si le type d'analyseur n'est pas enregistré
    """
    registry = AnalyzerRegistration.get_instance()
    analyzer_class = registry.get_analyzer(analyzer_type)
    return analyzer_class({})  # Empty context for now

def get_available_analyzers() -> Dict[str, str]:
    """
    Retourne la liste des analyseurs disponibles avec leurs descriptions.
    
    Returns:
        Dict avec les types d'analyseurs et leurs descriptions
    """
    return AnalyzerRegistration.get_available_analyzers()

def register_custom_analyzer(
    analyzer_type: AnalyzerType,
    analyzer_class: Type[Analyzer]
) -> None:
    """
    Enregistre un analyseur personnalisé.
    
    Args:
        analyzer_type: Type d'analyseur à enregistrer
        analyzer_class: Classe d'analyseur à associer au type
        
    Raises:
        ValueError: Si le type est déjà enregistré ou si la classe ne respecte pas l'interface
    """
    AnalyzerRegistration.register_analyzer(analyzer_type, analyzer_class)

# Initialiser le système d'analyse au chargement du module
initialize_analyzers()
