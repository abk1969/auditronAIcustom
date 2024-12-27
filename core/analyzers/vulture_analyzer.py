"""Analyseur de code mort utilisant Vulture."""
import subprocess
import json
import tempfile
from typing import Dict, Any, List
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class VultureAnalyzer(BaseAnalyzer):
    """Analyseur de code mort utilisant l'outil Vulture."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.DEAD_CODE

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        try:
            # Vérifier que Vulture est installé
            subprocess.run(
                ["vulture", "--version"],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error("Vulture n'est pas installé ou accessible")
            raise RuntimeError("Vulture n'est pas disponible") from e
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de Vulture: {str(e)}")
            raise

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse du code mort.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Créer un fichier temporaire avec le code
            temp_file = self._create_temp_file(self.context.code, '.py')
            
            # Exécuter Vulture avec sortie JSON
            process = subprocess.run(
                [
                    "vulture",
                    "--min-confidence", "80",
                    "--json",
                    temp_file
                ],
                capture_output=True,
                text=True,
                check=False
            )
            
            # Analyser la sortie
            if process.stdout:
                results = json.loads(process.stdout)
                return self._process_results(results)
            
            # Gérer les erreurs
            if process.returncode != 0 and process.stderr:
                logger.error(f"Erreur Vulture: {process.stderr}")
                return {
                    "error": True,
                    "message": process.stderr
                }
            
            return self._create_empty_results()
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            return {
                "error": True,
                "message": "Erreur lors de l'analyse des résultats"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Vulture: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse du code mort: {str(e)}",
                vulnerability_type="dead_code_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _process_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Traite les résultats bruts de Vulture.
        
        Args:
            results: Résultats JSON de Vulture
            
        Returns:
            Dict contenant les résultats formatés
        """
        # Initialiser les compteurs
        stats = {
            'total_items': len(results),
            'unused_vars': 0,
            'unused_funcs': 0,
            'unused_classes': 0,
            'unused_imports': 0,
            'unused_props': 0,
            'confidence_avg': 0.0
        }
        
        # Classifier les éléments non utilisés
        unused_vars = []
        unused_funcs = []
        unused_classes = []
        unused_imports = []
        unused_props = []
        total_confidence = 0.0
        
        for item in results:
            confidence = item.get('confidence', 0)
            total_confidence += confidence
            
            item_type = item.get('type', '').lower()
            if item_type == 'variable':
                unused_vars.append(self._format_item(item))
                stats['unused_vars'] += 1
            elif item_type == 'function':
                unused_funcs.append(self._format_item(item))
                stats['unused_funcs'] += 1
            elif item_type == 'class':
                unused_classes.append(self._format_item(item))
                stats['unused_classes'] += 1
            elif item_type == 'import':
                unused_imports.append(self._format_item(item))
                stats['unused_imports'] += 1
            elif item_type == 'property':
                unused_props.append(self._format_item(item))
                stats['unused_props'] += 1
                
        # Calculer la moyenne de confiance
        if stats['total_items'] > 0:
            stats['confidence_avg'] = total_confidence / stats['total_items']
            
        return {
            'unused_vars': unused_vars,
            'unused_funcs': unused_funcs,
            'unused_classes': unused_classes,
            'unused_imports': unused_imports,
            'unused_props': unused_props,
            'stats': stats
        }

    def _format_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate un élément non utilisé.
        
        Args:
            item: Élément à formater
            
        Returns:
            Dict contenant l'élément formaté
        """
        return {
            'name': item.get('name', ''),
            'filename': item.get('filename', ''),
            'line_number': item.get('line_number', 0),
            'size': item.get('size', 0),
            'confidence': item.get('confidence', 0),
            'message': item.get('message', ''),
            'code': item.get('code', '')
        }

    def _create_empty_results(self) -> Dict[str, Any]:
        """
        Crée des résultats vides.
        
        Returns:
            Dict contenant des résultats vides
        """
        return {
            'unused_vars': [],
            'unused_funcs': [],
            'unused_classes': [],
            'unused_imports': [],
            'unused_props': [],
            'stats': {
                'total_items': 0,
                'unused_vars': 0,
                'unused_funcs': 0,
                'unused_classes': 0,
                'unused_imports': 0,
                'unused_props': 0,
                'confidence_avg': 0.0
            }
        }

    def _get_impact_level(self, item_type: str, confidence: float) -> str:
        """
        Détermine le niveau d'impact du code mort.
        
        Args:
            item_type: Type d'élément
            confidence: Niveau de confiance
            
        Returns:
            Niveau d'impact (high, medium, low)
        """
        if confidence >= 90:
            if item_type in {'class', 'function'}:
                return 'high'
            elif item_type == 'import':
                return 'medium'
            return 'low'
        elif confidence >= 70:
            if item_type in {'class', 'function', 'import'}:
                return 'medium'
            return 'low'
        return 'low'

    def _generate_fix_suggestion(self, item: Dict[str, Any]) -> str:
        """
        Génère une suggestion de correction.
        
        Args:
            item: Élément à corriger
            
        Returns:
            Suggestion de correction
        """
        item_type = item.get('type', '').lower()
        name = item.get('name', '')
        
        if item_type == 'import':
            return f"Supprimer l'import inutilisé '{name}'"
        elif item_type == 'variable':
            return f"Supprimer la variable inutilisée '{name}' ou l'utiliser"
        elif item_type == 'function':
            return f"Supprimer la fonction inutilisée '{name}' ou l'appeler"
        elif item_type == 'class':
            return f"Supprimer la classe inutilisée '{name}' ou l'instancier"
        elif item_type == 'property':
            return f"Supprimer la propriété inutilisée '{name}' ou l'accéder"
        
        return f"Supprimer l'élément inutilisé '{name}'"
