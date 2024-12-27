"""Analyseur de complexité de code utilisant Radon."""
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class RadonAnalyzer(BaseAnalyzer):
    """Analyseur de complexité de code utilisant l'outil Radon."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.COMPLEXITY

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        try:
            # Vérifier que Radon est installé
            subprocess.run(
                ["radon", "--version"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error("Radon n'est pas installé ou accessible")
            raise RuntimeError("Radon n'est pas disponible") from e
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de Radon: {str(e)}")
            raise

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse de complexité.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Créer un fichier temporaire avec le code
            temp_file = self._create_temp_file(self.context.code, '.py')
            
            # Analyser la complexité cyclomatique
            cc_results = self._analyze_cyclomatic_complexity(temp_file)
            
            # Analyser la complexité de Halstead
            hal_results = self._analyze_halstead_metrics(temp_file)
            
            # Analyser la maintenabilité
            mi_results = self._analyze_maintainability_index(temp_file)
            
            # Analyser les métriques brutes
            raw_results = self._analyze_raw_metrics(temp_file)
            
            return {
                'cyclomatic_complexity': cc_results,
                'halstead_metrics': hal_results,
                'maintainability_index': mi_results,
                'raw_metrics': raw_results
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Radon: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse de complexité: {str(e)}",
                vulnerability_type="complexity_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _analyze_cyclomatic_complexity(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyse la complexité cyclomatique.
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Liste des résultats de complexité
        """
        process = subprocess.run(
            [
                "radon",
                "cc",
                "--json",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.stdout:
            try:
                results = json.loads(process.stdout)
                return self._process_cc_results(results)
            except json.JSONDecodeError:
                logger.error("Erreur lors du parsing des résultats CC")
                
        return []

    def _analyze_halstead_metrics(self, file_path: str) -> Dict[str, Any]:
        """
        Analyse les métriques de Halstead.
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Dict contenant les métriques
        """
        process = subprocess.run(
            [
                "radon",
                "hal",
                "--json",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.stdout:
            try:
                results = json.loads(process.stdout)
                return self._process_hal_results(results)
            except json.JSONDecodeError:
                logger.error("Erreur lors du parsing des résultats HAL")
                
        return {}

    def _analyze_maintainability_index(self, file_path: str) -> Dict[str, float]:
        """
        Analyse l'index de maintenabilité.
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Dict contenant les indices
        """
        process = subprocess.run(
            [
                "radon",
                "mi",
                "--json",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.stdout:
            try:
                results = json.loads(process.stdout)
                return self._process_mi_results(results)
            except json.JSONDecodeError:
                logger.error("Erreur lors du parsing des résultats MI")
                
        return {}

    def _analyze_raw_metrics(self, file_path: str) -> Dict[str, int]:
        """
        Analyse les métriques brutes.
        
        Args:
            file_path: Chemin du fichier à analyser
            
        Returns:
            Dict contenant les métriques
        """
        process = subprocess.run(
            [
                "radon",
                "raw",
                "--json",
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.stdout:
            try:
                results = json.loads(process.stdout)
                return self._process_raw_results(results)
            except json.JSONDecodeError:
                logger.error("Erreur lors du parsing des résultats RAW")
                
        return {}

    def _process_cc_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Traite les résultats de complexité cyclomatique.
        
        Args:
            results: Résultats bruts
            
        Returns:
            Liste des résultats traités
        """
        processed = []
        for file_path, functions in results.items():
            for func in functions:
                processed.append({
                    'name': func['name'],
                    'complexity': func['complexity'],
                    'rank': self._get_complexity_rank(func['complexity']),
                    'line_number': func['lineno'],
                    'end_line': func.get('endline', func['lineno']),
                    'type': func['type']
                })
        return processed

    def _process_hal_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les résultats de Halstead.
        
        Args:
            results: Résultats bruts
            
        Returns:
            Dict contenant les résultats traités
        """
        processed = {}
        for file_path, metrics in results.items():
            processed = {
                'h1': metrics['h1'],  # Nombre d'opérateurs uniques
                'h2': metrics['h2'],  # Nombre d'opérandes uniques
                'N1': metrics['N1'],  # Nombre total d'opérateurs
                'N2': metrics['N2'],  # Nombre total d'opérandes
                'vocabulary': metrics['vocabulary'],
                'length': metrics['length'],
                'calculated_length': metrics['calculated_length'],
                'volume': metrics['volume'],
                'difficulty': metrics['difficulty'],
                'effort': metrics['effort'],
                'time': metrics['time'],
                'bugs': metrics['bugs']
            }
        return processed

    def _process_mi_results(self, results: Dict[str, Any]) -> Dict[str, float]:
        """
        Traite les résultats de maintenabilité.
        
        Args:
            results: Résultats bruts
            
        Returns:
            Dict contenant les résultats traités
        """
        processed = {}
        for file_path, mi in results.items():
            processed = {
                'maintainability_index': float(mi),
                'rank': self._get_maintainability_rank(float(mi))
            }
        return processed

    def _process_raw_results(self, results: Dict[str, Any]) -> Dict[str, int]:
        """
        Traite les résultats bruts.
        
        Args:
            results: Résultats bruts
            
        Returns:
            Dict contenant les résultats traités
        """
        processed = {}
        for file_path, metrics in results.items():
            processed = {
                'loc': metrics['loc'],
                'lloc': metrics['lloc'],
                'sloc': metrics['sloc'],
                'comments': metrics['comments'],
                'multi': metrics['multi'],
                'blank': metrics['blank'],
                'single_comments': metrics['single_comments']
            }
        return processed

    def _get_complexity_rank(self, complexity: int) -> str:
        """
        Détermine le rang de complexité.
        
        Args:
            complexity: Score de complexité
            
        Returns:
            Rang de complexité (A-F)
        """
        if complexity <= 5:
            return 'A'
        elif complexity <= 10:
            return 'B'
        elif complexity <= 20:
            return 'C'
        elif complexity <= 30:
            return 'D'
        elif complexity <= 40:
            return 'E'
        return 'F'

    def _get_maintainability_rank(self, mi: float) -> str:
        """
        Détermine le rang de maintenabilité.
        
        Args:
            mi: Index de maintenabilité
            
        Returns:
            Rang de maintenabilité (A-C)
        """
        if mi >= 20:
            return 'A'
        elif mi >= 10:
            return 'B'
        return 'C'

    def _get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """
        Génère une suggestion de correction.
        
        Args:
            issue: Problème à corriger
            
        Returns:
            Suggestion de correction
        """
        if 'complexity' in issue:
            complexity = issue['complexity']
            if complexity > 40:
                return "Diviser la fonction en plusieurs fonctions plus petites"
            elif complexity > 30:
                return "Réduire la complexité en simplifiant la logique conditionnelle"
            elif complexity > 20:
                return "Considérer la refactorisation pour réduire la complexité"
            elif complexity > 10:
                return "Examiner les opportunités de simplification"
                
        if 'maintainability_index' in issue:
            mi = issue['maintainability_index']
            if mi < 10:
                return "Améliorer la documentation et réduire la complexité"
            elif mi < 20:
                return "Ajouter des commentaires et simplifier le code"
                
        if 'effort' in issue:
            effort = issue['effort']
            if effort > 1000:
                return "Simplifier la logique et réduire le nombre d'opérateurs"
                
        return "Revoir le code pour améliorer sa maintenabilité"
