"""Module d'analyse de sécurité."""
from typing import Dict, Any, Optional
import os
import tempfile
import bandit
from bandit.core.manager import BanditManager
from bandit.core.config import BanditConfig
from safety.safety import check as safety_check
from safety.util import read_requirements
from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType, AnalyzerContext
from ..logger import logger

class SecurityAnalyzer(BaseAnalyzer):
    """Analyseur de sécurité combinant plusieurs outils."""
    
    analyzer_type = AnalyzerType.SECURITY
    
    def __init__(self):
        """Initialise l'analyseur de sécurité."""
        super().__init__()
        self.bandit_config = BanditConfig()
        self._temp_file: Optional[str] = None
        
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
        Effectue l'analyse de sécurité.
        
        Returns:
            Dict contenant les résultats d'analyse
        """
        if not self._temp_file or not os.path.exists(self._temp_file):
            raise RuntimeError("Fichier temporaire non disponible")
            
        results = {
            'issues': [],
            'metrics': {},
            'dependencies': {},
            'coverage': 0
        }
        
        try:
            # Analyse avec Bandit
            manager = BanditManager(self.bandit_config, 'file')
            manager.discover_files([self._temp_file])
            manager.run_tests()
            
            # Collecter les résultats
            issues = []
            for issue in manager.get_issue_list():
                issues.append({
                    'severity': issue.severity,
                    'confidence': issue.confidence,
                    'title': issue.test_id,
                    'description': issue.text,
                    'line': issue.line_number,
                    'code': self._context.code.splitlines()[issue.line_number - 1] if issue.line_number > 0 else ''
                })
                
            # Métriques
            metrics = {
                'total_issues': len(issues),
                'critical': len([i for i in issues if i['severity'] == 'CRITICAL']),
                'high': len([i for i in issues if i['severity'] == 'HIGH']),
                'medium': len([i for i in issues if i['severity'] == 'MEDIUM']),
                'low': len([i for i in issues if i['severity'] == 'LOW'])
            }
            
            results['issues'] = issues
            results['metrics'] = metrics
            
            # Analyse des dépendances si c'est un fichier requirements.txt
            if self._context.filename.endswith('requirements.txt'):
                results['dependencies'] = await self._check_dependencies()
                
            # Calcul de la couverture
            results['coverage'] = self._calculate_coverage(results)
            
            # Ajouter des informations supplémentaires
            results['status'] = 'success'
            if not issues:
                results['message'] = "Aucun problème de sécurité détecté"
            else:
                results['message'] = f"Détection de {len(issues)} problème(s) de sécurité"
                
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sécurité: {str(e)}")
            return {
                'status': 'error',
                'message': f"Erreur lors de l'analyse: {str(e)}",
                'issues': [],
                'metrics': {},
                'coverage': 0
            }
            
    async def _check_dependencies(self) -> Dict[str, Any]:
        """
        Vérifie les vulnérabilités dans les dépendances.
        
        Returns:
            Résultats de l'analyse des dépendances
        """
        try:
            vulns = safety_check(read_requirements([self._temp_file]))
            return {
                'vulnerabilities': [
                    {
                        'package': vuln.package,
                        'version': vuln.version,
                        'description': vuln.description,
                        'severity': vuln.severity
                    }
                    for vuln in vulns
                ],
                'total': len(vulns)
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des dépendances: {str(e)}")
            return {
                'vulnerabilities': [],
                'total': 0,
                'error': str(e)
            }
            
    def _calculate_coverage(self, results: Dict[str, Any]) -> float:
        """
        Calcule un score de couverture de sécurité.
        
        Args:
            results: Résultats d'analyse
            
        Returns:
            Score entre 0 et 100
        """
        total_issues = results['metrics'].get('total_issues', 0)
        if total_issues == 0:
            return 100.0
            
        # Pondération des problèmes par sévérité
        weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.1
        }
        
        # Calculer le score
        weighted_sum = sum(
            results['metrics'].get(severity, 0) * weight
            for severity, weight in weights.items()
        )
        
        # Normaliser entre 0 et 100
        score = max(0, 100 - (weighted_sum / total_issues * 100))
        
        # Pénaliser pour les vulnérabilités dans les dépendances
        if results.get('dependencies', {}).get('total', 0) > 0:
            score *= 0.9  # 10% de pénalité
            
        return round(score, 2)
        
    async def _cleanup_impl(self) -> None:
        """Nettoie les ressources spécifiques à l'analyseur de sécurité."""
        self._temp_file = None
