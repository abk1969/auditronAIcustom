"""Plugin d'analyse TypeScript."""
from typing import Dict, Any
from .base import AnalysisPlugin
from ...analyzers.typescript_analyzer import TypeScriptAnalyzer
from ...config.analyzer_config import AnalyzerConfig

class TypeScriptAnalysisPlugin(AnalysisPlugin):
    """Plugin pour l'analyse de code TypeScript."""

    def __init__(self):
        """Initialise le plugin avec l'analyseur TypeScript."""
        self.analyzer = TypeScriptAnalyzer()

    def analyze(self, code: str, filename: str = "code.ts") -> Dict[str, Any]:
        """
        Analyse le code TypeScript.
        
        Args:
            code (str): Code source à analyser
            filename (str): Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse incluant:
                - security_issues: Liste des problèmes de sécurité
                - quality_issues: Liste des problèmes de qualité
                - complexity_score: Score de complexité
                - maintainability_score: Score de maintenabilité
        """
        if not code.strip():
            return {
                'error': 'Le code ne peut pas être vide',
                'security_issues': [],
                'quality_issues': [],
                'complexity_score': 0,
                'maintainability_score': 0
            }

        # Vérifie si c'est du TypeScript
        if not filename.endswith('.ts') and not filename.endswith('.tsx'):
            return {
                'error': 'Ce plugin ne prend en charge que les fichiers TypeScript (.ts/.tsx)',
                'security_issues': [],
                'quality_issues': [],
                'complexity_score': 0,
                'maintainability_score': 0
            }

        try:
            results = self.analyzer.analyze(code, filename)
            
            # Formatage des résultats
            formatted_results = {
                'error': None,
                'security_issues': results.get('security_issues', []),
                'quality_issues': results.get('quality_issues', []),
                'complexity_score': results.get('complexity_score', 0),
                'maintainability_score': results.get('maintainability_score', 0),
                'total_issues': (
                    len(results.get('security_issues', [])) +
                    len(results.get('quality_issues', []))
                )
            }

            # Ajout de métriques supplémentaires
            if 'quality' in results:
                formatted_results.update({
                    'code_quality': {
                        'complexity': results['quality'].get('complexity_score', 0),
                        'maintainability': results['quality'].get('maintainability_score', 0),
                        'issues': results['quality'].get('quality_issues', [])
                    }
                })

            return formatted_results

        except Exception as e:
            return {
                'error': f"Erreur lors de l'analyse TypeScript: {str(e)}",
                'security_issues': [],
                'quality_issues': [],
                'complexity_score': 0,
                'maintainability_score': 0
            }

    def cleanup(self):
        """Nettoie les ressources utilisées par le plugin."""
        if self.analyzer:
            self.analyzer.cleanup()
