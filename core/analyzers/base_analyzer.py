"""Classe de base abstraite pour tous les analyseurs."""
import os
import tempfile
from abc import abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from .interfaces import Analyzer, AnalyzerContext, AnalyzerType
from ..logger import logger
from ..config.analyzer_config import AnalyzerConfig

class BaseAnalyzer(Analyzer):
    """Classe de base abstraite fournissant les fonctionnalités communes aux analyseurs."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        """
        Initialise l'analyseur avec des valeurs par défaut.
        
        Args:
            config: Configuration optionnelle pour l'analyseur
        """
        self._context: Optional[AnalyzerContext] = None
        self._temp_files: list[str] = []
        self._initialized = False
        self._config = config

    async def initialize(self, context: AnalyzerContext) -> None:
        """
        Initialise l'analyseur avec le contexte fourni.
        
        Args:
            context: Contexte d'exécution pour l'analyse
            
        Raises:
            RuntimeError: Si l'analyseur est déjà initialisé
        """
        if self._initialized:
            raise RuntimeError("L'analyseur est déjà initialisé")
            
        self._context = context
        self._initialized = True
        await self._setup()

    @abstractmethod
    async def _setup(self) -> None:
        """
        Configure l'analyseur après l'initialisation.
        À implémenter par les classes dérivées.
        """
        pass

    async def analyze(self) -> Dict[str, Any]:
        """
        Effectue l'analyse du code.
        
        Returns:
            Dictionnaire contenant les résultats de l'analyse
            
        Raises:
            RuntimeError: Si l'analyseur n'est pas initialisé
        """
        if not self._initialized:
            raise RuntimeError("L'analyseur n'est pas initialisé")
            
        try:
            return await self._analyze_impl()
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse {self.analyzer_type}: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "analyzer": self.analyzer_type.value
            }

    @abstractmethod
    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Implémentation spécifique de l'analyse.
        À implémenter par les classes dérivées.
        
        Returns:
            Dictionnaire contenant les résultats de l'analyse
        """
        pass

    async def cleanup(self) -> None:
        """Nettoie les ressources utilisées par l'analyseur."""
        try:
            for temp_file in self._temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            self._temp_files.clear()
            
            await self._cleanup_impl()
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de l'analyseur {self.analyzer_type}: {str(e)}")
            
        finally:
            self._initialized = False
            self._context = None

    async def _cleanup_impl(self) -> None:
        """
        Implémentation spécifique du nettoyage.
        Peut être surchargée par les classes dérivées si nécessaire.
        """
        pass

    def _create_temp_file(self, content: str, suffix: str = None) -> str:
        """
        Crée un fichier temporaire avec le contenu spécifié.
        
        Args:
            content: Contenu à écrire dans le fichier
            suffix: Suffixe optionnel pour le fichier (ex: '.py')
            
        Returns:
            Chemin vers le fichier temporaire créé
        """
        if not self._context:
            raise RuntimeError("Contexte non initialisé")
            
        temp_dir = self._context.temp_dir or tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=suffix,
            dir=temp_dir,
            delete=False
        ) as temp_file:
            temp_file.write(content)
            self._temp_files.append(temp_file.name)
            return temp_file.name

    @property
    def context(self) -> AnalyzerContext:
        """Retourne le contexte d'exécution."""
        if not self._context:
            raise RuntimeError("Contexte non initialisé")
        return self._context

    @property
    @abstractmethod
    def analyzer_type(self) -> AnalyzerType:
        """
        Retourne le type d'analyseur.
        À implémenter par les classes dérivées.
        """
        pass
