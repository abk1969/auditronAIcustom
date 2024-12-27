"""Interfaces et types pour les analyseurs."""
from enum import Enum, auto
from typing import Dict, Any, Protocol, runtime_checkable, List

class AnalyzerType(Enum):
    """Types d'analyseurs disponibles."""
    
    # Analyseur de scripts génériques
    SCRIPT = auto()
    
    # Analyseur de code inutilisé
    UNUSED = auto()
    
    # Analyseur de qualité de code
    QUALITY = auto()
    
    # Analyseur TypeScript
    TYPESCRIPT = auto()
    
    # Analyseur SQL
    SQL = auto()
    
    # Analyseur de complexité
    COMPLEXITY = auto()
    
    # Analyseur de sécurité
    SECURITY = auto()

@runtime_checkable
class Analyzer(Protocol):
    """Interface de base pour les analyseurs."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """
        Retourne le type d'analyseur.
        
        Returns:
            Type d'analyseur
        """
        ...

    async def analyze(self) -> Dict[str, Any]:
        """
        Effectue l'analyse.
        
        Returns:
            Résultats de l'analyse
            
        Raises:
            SecurityError: En cas d'erreur lors de l'analyse
        """
        ...

    async def setup(self) -> None:
        """
        Configure l'analyseur.
        
        Raises:
            SecurityError: En cas d'erreur de configuration
        """
        ...

@runtime_checkable
class AnalyzerContext(Protocol):
    """Interface pour le contexte d'analyse."""

    @property
    def code(self) -> str:
        """
        Code source à analyser.
        
        Returns:
            Code source
        """
        ...

    @property
    def filename(self) -> str:
        """
        Nom du fichier analysé.
        
        Returns:
            Nom du fichier
        """
        ...

    @property
    def language(self) -> str:
        """
        Langage du code.
        
        Returns:
            Langage (python, typescript, sql, etc.)
        """
        ...

    @property
    def config(self) -> Dict[str, Any]:
        """
        Configuration de l'analyseur.
        
        Returns:
            Configuration
        """
        ...

@runtime_checkable
class AnalyzerResult(Protocol):
    """Interface pour les résultats d'analyse."""

    @property
    def issues(self) -> List[Dict[str, Any]]:
        """
        Problèmes détectés.
        
        Returns:
            Liste des problèmes
        """
        ...

    @property
    def metrics(self) -> Dict[str, Any]:
        """
        Métriques calculées.
        
        Returns:
            Métriques
        """
        ...

    @property
    def summary(self) -> Dict[str, Any]:
        """
        Résumé de l'analyse.
        
        Returns:
            Résumé
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit les résultats en dictionnaire.
        
        Returns:
            Résultats au format dict
        """
        ...

    def merge(self, other: 'AnalyzerResult') -> None:
        """
        Fusionne avec d'autres résultats.
        
        Args:
            other: Résultats à fusionner
        """
        ...
