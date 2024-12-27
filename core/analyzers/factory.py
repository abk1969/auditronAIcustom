"""Factory pour la création d'analyseurs."""
from typing import Dict, Any, Type, List

from .interfaces import AnalyzerType
from .base_analyzer import BaseAnalyzer
from .registry import default_registry, AnalyzerRegistration
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class AnalyzerFactory:
    """Factory pour créer des instances d'analyseurs."""

    @staticmethod
    async def create_analyzer(
        analyzer_type: AnalyzerType,
        context: Dict[str, Any]
    ) -> BaseAnalyzer:
        """
        Crée une instance d'analyseur.
        
        Args:
            analyzer_type: Type d'analyseur à créer
            context: Contexte d'analyse
            
        Returns:
            Instance d'analyseur configurée
            
        Raises:
            SecurityError: Si la création échoue
        """
        try:
            # Récupérer la classe d'analyseur depuis le registre
            analyzer_class = default_registry.get_analyzer(analyzer_type)
            
            # Créer et configurer l'instance
            analyzer = analyzer_class(context)
            await analyzer._setup()
            
            return analyzer
            
        except KeyError as e:
            logger.error(f"Type d'analyseur non supporté: {analyzer_type}")
            raise SecurityError(
                message=f"Type d'analyseur non supporté: {analyzer_type}",
                vulnerability_type="analyzer_creation_error",
                severity=ErrorSeverity.ERROR
            ) from e
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'analyseur: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de la création de l'analyseur: {str(e)}",
                vulnerability_type="analyzer_creation_error",
                severity=ErrorSeverity.ERROR
            ) from e

    @staticmethod
    async def create_analyzers(
        analyzer_types: List[AnalyzerType],
        context: Dict[str, Any]
    ) -> List[BaseAnalyzer]:
        """
        Crée plusieurs instances d'analyseurs.
        
        Args:
            analyzer_types: Types d'analyseurs à créer
            context: Contexte d'analyse
            
        Returns:
            Liste d'instances d'analyseurs configurées
            
        Raises:
            SecurityError: Si la création d'un analyseur échoue
        """
        analyzers = []
        for analyzer_type in analyzer_types:
            analyzer = await AnalyzerFactory.create_analyzer(analyzer_type, context)
            analyzers.append(analyzer)
        return analyzers

    @staticmethod
    def get_available_analyzers() -> Dict[AnalyzerType, Type[BaseAnalyzer]]:
        """
        Récupère tous les analyseurs disponibles.
        
        Returns:
            Dict des analyseurs par type
        """
        return default_registry.get_all_analyzers()

    @staticmethod
    def register_analyzer(
        analyzer_type: AnalyzerType,
        analyzer_class: Type[BaseAnalyzer]
    ) -> None:
        """
        Enregistre un nouvel analyseur.
        
        Args:
            analyzer_type: Type d'analyseur
            analyzer_class: Classe d'analyseur
        """
        default_registry.register(analyzer_type, analyzer_class)

    @staticmethod
    def unregister_analyzer(analyzer_type: AnalyzerType) -> None:
        """
        Supprime un analyseur du registre.
        
        Args:
            analyzer_type: Type d'analyseur à supprimer
        """
        default_registry.unregister(analyzer_type)

    @staticmethod
    def clear_analyzers() -> None:
        """Supprime tous les analyseurs du registre."""
        default_registry.clear()
