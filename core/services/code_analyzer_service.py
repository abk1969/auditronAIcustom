"""Service pour l'analyse de code."""
from typing import Dict, Any, List, Type
from AuditronAI.core.logger import setup_logging
from .analysis_plugins.base import AnalysisPlugin
from .plugin_registry import PluginRegistry

logger = setup_logging()

class CodeAnalyzerService:
    """Service responsable de l'analyse de code utilisant différents plugins."""
    
    def __init__(self):
        """Initialise le service avec les plugins d'analyse."""
        self.plugins: Dict[str, AnalysisPlugin] = {}
        # Charge les plugins enregistrés
        for name, plugin_class in PluginRegistry.list_plugins().items():
            self.plugins[name] = plugin_class()
    
    def analyze(self, code: str, filename: str = "code.py") -> Dict[str, Any]:
        """
        Effectue une analyse complète du code incluant sécurité et métriques.
        
        Args:
            code (str): Code source à analyser
            filename (str): Nom du fichier analysé
            
        Returns:
            Dict[str, Any]: Résultats d'analyse incluant sécurité et métriques
            
        Raises:
            ValueError: Si le code est vide ou invalide
            RuntimeError: Si l'analyse échoue
        """
        if not code.strip():
            raise ValueError("Le code ne peut pas être vide")
            
        try:
            analysis_result = {
                "file": filename,
                "code": code
            }
            
            # Exécute chaque plugin d'analyse
            for name, plugin in self.plugins.items():
                    
                try:
                    result = plugin.analyze(code, filename)
                    analysis_result[name] = result
                except Exception as e:
                    logger.error(f"Erreur dans le plugin {name}: {str(e)}")
                    analysis_result[name] = {"error": str(e)}
            
            logger.info(f"Analyse complétée avec succès pour {filename}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erreur d'analyse: {str(e)}")
            raise RuntimeError(f"L'analyse a échoué: {str(e)}")
            
    def register_plugin(self, name: str, plugin_class: Type[AnalysisPlugin]):
        """
        Enregistre un nouveau plugin d'analyse.
        
        Args:
            name: Nom unique du plugin
            plugin_class: Classe du plugin
        """
        PluginRegistry.register(name, plugin_class)
        self.plugins[name] = plugin_class()
