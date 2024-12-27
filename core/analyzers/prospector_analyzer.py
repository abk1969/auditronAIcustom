"""Module d'analyse de qualité avec Prospector."""
from typing import Dict, Any, Optional
import os
import tempfile
import json
from prospector.run import Prospector
from prospector.config import ProspectorConfig
from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType, AnalyzerContext
from ..logger import logger

class ProspectorAnalyzer(BaseAnalyzer):
    """Analyseur de qualité de code utilisant Prospector."""
    
    analyzer_type = AnalyzerType.QUALITY
    
    def __init__(self):
        """Initialise l'analyseur Prospector."""
        super().__init__()
        self._temp_file: Optional[str] = None
        self._config = ProspectorConfig()
        
        # Configuration par défaut
        self._config.profile.disable_tool('pyroma')  # Désactiver pyroma car il nécessite un package
        self._config.profile.disable_tool('vulture')  # On a déjà un analyseur dédié
        
    async def _setup(self) -> None:
        """Configure l'analyseur après l'initialisation."""
        if not self._context:
            raise RuntimeError("Contexte d'analyse non initialisé")
            
        # Créer un fichier temporaire pour l'analyse
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(self._context.code)
            self._temp_file = temp_file.name
            self._temp_files.append(self._temp_file)
            
    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse de qualité avec Prospector.
        
        Returns:
            Dict contenant les résultats d'analyse
        """
        if not self._temp_file or not os.path.exists(self._temp_file):
            raise RuntimeError("Fichier temporaire non disponible")
            
        results = {
            'issues': [],
            'metrics': {},
            'tools': {},
            'coverage': 0
        }
        
        try:
            # Initialiser Prospector
            prospector = Prospector(
                paths=[self._temp_file],
                config=self._config,
                profile_path=None,
                strictness='medium'
            )
            
            # Lancer l'analyse
            prospector.execute()
            
            # Collecter les résultats
            issues = []
            tools_stats = {}
            
            for message in prospector.get_messages():
                tool = message.source
                if tool not in tools_stats:
                    tools_stats[tool] = {'total': 0, 'by_type': {}}
                    
                msg_type = message.message_type or 'unknown'
                if msg_type not in tools_stats[tool]['by_type']:
                    tools_stats[tool]['by_type'][msg_type] = 0
                    
                tools_stats[tool]['total'] += 1
                tools_stats[tool]['by_type'][msg_type] += 1
                
                issues.append({
                    'tool': tool,
                    'type': msg_type,
                    'message': message.message,
                    'line': message.line or 0,
                    'character': message.character or 0,
                    'code': self._context.code.splitlines()[message.line - 1] if message.line else ''
                })
                
            # Calculer les métriques
            metrics = {
                'total_issues': len(issues),
                'tools_used': len(tools_stats),
                'issues_by_tool': {tool: stats['total'] for tool, stats in tools_stats.items()},
                'issues_by_type': self._aggregate_issues_by_type(tools_stats)
            }
            
            results['issues'] = issues
            results['metrics'] = metrics
            results['tools'] = tools_stats
            
            # Calculer la couverture
            results['coverage'] = self._calculate_coverage(results)
            
            # Ajouter des informations supplémentaires
            results['status'] = 'success'
            if not issues:
                results['message'] = "Aucun problème de qualité détecté"
            else:
                results['message'] = f"Détection de {len(issues)} problème(s) de qualité"
                
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Prospector: {str(e)}")
            return {
                'status': 'error',
                'message': f"Erreur lors de l'analyse: {str(e)}",
                'issues': [],
                'metrics': {},
                'coverage': 0
            }
            
    def _aggregate_issues_by_type(self, tools_stats: Dict[str, Dict]) -> Dict[str, int]:
        """
        Agrège les problèmes par type tous outils confondus.
        
        Args:
            tools_stats: Statistiques par outil
            
        Returns:
            Dict avec le compte total par type de problème
        """
        aggregated = {}
        for tool_stats in tools_stats.values():
            for msg_type, count in tool_stats['by_type'].items():
                if msg_type not in aggregated:
                    aggregated[msg_type] = 0
                aggregated[msg_type] += count
        return aggregated
        
    def _calculate_coverage(self, results: Dict[str, Any]) -> float:
        """
        Calcule un score de qualité basé sur les résultats.
        
        Args:
            results: Résultats d'analyse
            
        Returns:
            Score entre 0 et 100
        """
        total_issues = results['metrics'].get('total_issues', 0)
        if total_issues == 0:
            return 100.0
            
        # Pondération par type de problème
        weights = {
            'error': 1.0,
            'warning': 0.7,
            'convention': 0.4,
            'refactor': 0.3,
            'info': 0.1,
            'unknown': 0.5
        }
        
        # Calculer le score
        weighted_sum = 0
        for msg_type, count in results['metrics']['issues_by_type'].items():
            weight = weights.get(msg_type.lower(), weights['unknown'])
            weighted_sum += count * weight
            
        # Normaliser entre 0 et 100
        score = max(0, 100 - (weighted_sum / total_issues * 100))
        
        return round(score, 2)
        
    async def _cleanup_impl(self) -> None:
        """Nettoie les ressources spécifiques à l'analyseur Prospector."""
        self._temp_file = None
