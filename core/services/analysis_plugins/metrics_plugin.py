"""Plugin d'analyse des métriques de code."""
from typing import Dict, Any
import ast
from AuditronAI.core.services.analysis_plugins.base import AnalysisPlugin
from AuditronAI.core.logger import setup_logging

logger = setup_logging()

class MetricsPlugin(AnalysisPlugin):
    """Plugin pour l'analyse des métriques du code."""
    
    def analyze(self, code: str, filename: str) -> Dict[str, Any]:
        """
        Calcule les métriques du code.
        
        Args:
            code: Code source à analyser
            filename: Nom du fichier
            
        Returns:
            Dict contenant les métriques calculées
        """
        try:
            tree = ast.parse(code)
            
            # Initialisation des compteurs
            metrics = {
                'loc': len(code.splitlines()),
                'functions': 0,
                'classes': 0,
                'complexity': 0,
                'imports': 0,
                'comments': 0
            }
            
            # Analyse de l'AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                    metrics['complexity'] += self._calculate_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    metrics['imports'] += 1
                    
            # Compter les commentaires
            for line in code.splitlines():
                if line.strip().startswith('#'):
                    metrics['comments'] += 1
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {str(e)}")
            return {
                'loc': 0,
                'functions': 0,
                'classes': 0,
                'complexity': 0,
                'imports': 0,
                'comments': 0,
                'error': str(e)
            }
            
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calcule la complexité cyclomatique d'une fonction.
        
        Args:
            node: Noeud AST de la fonction
            
        Returns:
            Complexité cyclomatique
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Branches qui augmentent la complexité
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
                
        return complexity
