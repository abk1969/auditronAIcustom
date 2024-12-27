"""Plugin d'analyse de sécurité."""
from typing import Dict, Any
from AuditronAI.core.services.analysis_plugins.base import AnalysisPlugin
from AuditronAI.core.analyzers.security_analyzer import SecurityAnalyzer
from AuditronAI.core.logger import setup_logging

logger = setup_logging()

class SecurityPlugin(AnalysisPlugin):
    """Plugin pour l'analyse de sécurité du code Python."""
    
    def __init__(self):
        """Initialise le plugin avec l'analyseur de sécurité."""
        self.analyzer = SecurityAnalyzer()
        
    def analyze(self, code: str, filename: str) -> Dict[str, Any]:
        """
        Effectue une analyse de sécurité du code.
        
        Args:
            code: Code source à analyser
            filename: Nom du fichier
            
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Utiliser l'analyseur de sécurité
            results = self.analyzer.analyze(code, filename)
            
            # Ajouter des informations supplémentaires
            if 'error' not in results:
                results['status'] = 'success'
                if not results['issues']:
                    results['message'] = "Aucun problème de sécurité détecté"
                else:
                    results['message'] = f"Détection de {len(results['issues'])} problème(s) de sécurité"
            else:
                results['status'] = 'error'
                results['message'] = f"Erreur lors de l'analyse: {results['error']}"
                
            return results
            
        except Exception as e:
            logger.error(f"Erreur dans le plugin de sécurité: {str(e)}")
            return {
                'status': 'error',
                'message': f"Erreur inattendue: {str(e)}",
                'issues': [],
                'metrics': {},
                'coverage': 0
            }
