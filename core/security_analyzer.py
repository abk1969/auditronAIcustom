"""
Module d'analyse de sécurité pour AuditronAI.

Ce module fournit des outils pour analyser la sécurité du code Python :
- Analyse de vulnérabilités avec Bandit
- Analyse de complexité avec Radon
- Détection de code mort avec Vulture
- Analyse de qualité avec Prospector
"""
# Imports de base
import os
import tempfile
from typing import Dict, Any

# Imports pour le logging
from .logger import logger

# Imports pour l'analyse de sécurité
from bandit.core import manager as bandit_manager
from bandit.core import config as b_config

# Imports pour l'analyse de code
import radon.complexity as radon
import vulture
from prospector.config import ProspectorConfig
from prospector.run import Prospector

from .bandit_config import get_bandit_config

class SecurityAnalyzer:
    """
    Classe principale pour l'analyse de sécurité du code.
    
    Cette classe combine plusieurs outils d'analyse :
    - Bandit pour les vulnérabilités de sécurité
    - Radon pour la complexité cyclomatique
    - Vulture pour la détection de code mort
    - Prospector pour la qualité du code
    """
    def __init__(self):
        """Initialise l'analyseur de sécurité."""
        # Configuration de base
        self.scan_level = os.getenv('SECURITY_SCAN_LEVEL', 'high')
        self.enable_deps = os.getenv('ENABLE_DEPENDENCY_CHECK', 'true').lower() == 'true'
        self.enable_static = os.getenv('ENABLE_STATIC_ANALYSIS', 'true').lower() == 'true'
        self.timeout = int(os.getenv('SECURITY_TIMEOUT', 30))
        
        # Seuils de sévérité
        self.severity_thresholds = {
            'critical': int(os.getenv('CRITICAL_SEVERITY_THRESHOLD', 0)),
            'high': int(os.getenv('HIGH_SEVERITY_THRESHOLD', 2)),
            'medium': int(os.getenv('MEDIUM_SEVERITY_THRESHOLD', 5)),
            'low': int(os.getenv('LOW_SEVERITY_THRESHOLD', 10))
        }
        
        # Configuration des analyses
        self.max_issues = int(os.getenv('SECURITY_MAX_ISSUES', 100))
        self.min_confidence = float(os.getenv('SECURITY_MIN_CONFIDENCE', 0.8))
        self.max_complexity = int(os.getenv('MAX_COMPLEXITY', 10))
        
        # Configuration Bandit
        self.bandit_profile = os.getenv('BANDIT_PROFILE', 'default')
        self.bandit_tests = os.getenv('BANDIT_TESTS', '').split(',')
        
        # Créer la configuration Bandit
        bandit_conf = get_bandit_config(
            scan_level=self.scan_level,
            min_confidence=self.min_confidence,
            max_issues=self.max_issues,
            profile=self.bandit_profile,
            tests=self.bandit_tests
        )
        
        # Initialiser la configuration
        self.bandit_config = b_config.BanditConfig()
        for key, value in bandit_conf.items():
            if value is not None:  # Ne pas définir les valeurs None
                setattr(self.bandit_config, key, value)
        
        # Configuration Pylint
        self.pylint_args = [
            "--disable=all",
            "--enable=security",
            "--exit-zero",
            "--output-format=json"
        ]

    def run_bandit_analysis(self, code: str, filename: str) -> Dict:
        """Exécute l'analyse de sécurité avec Bandit."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            try:
                mgr = bandit_manager.BanditManager(self.bandit_config, 'file')
                mgr.discover_files([temp_path])
                mgr.run_tests()
                
                return {
                    'issues': [
                        {
                            'severity': issue.severity,
                            'confidence': issue.confidence,
                            'test_name': issue.test_id,
                            'description': issue.text,
                            'line_number': issue.line_number
                        }
                        for issue in mgr.get_issue_list()
                    ]
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'exécution de Bandit : {str(e)}")
                return {'error': str(e), 'issues': []}
            
        finally:
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du fichier temporaire : {str(e)}")

    def run_radon_analysis(self, code: str) -> Dict:
        """
        Analyse la complexité cyclomatique avec Radon.

        Args:
            code (str): Le code source à analyser

        Returns:
            Dict: Résultats de l'analyse contenant :
                - average_complexity: Complexité moyenne
                - functions: Liste des fonctions avec leur complexité
                - error: Message d'erreur en cas de problème
        """
        try:
            # Analyse de complexité cyclomatique
            complexity = radon.cc_visit(code)
            results = {
                'average_complexity': sum(cc.complexity for cc in complexity) / len(complexity) if complexity else 0,
                'functions': [
                    {
                        'name': cc.name,
                        'complexity': cc.complexity,
                        'line': cc.lineno
                    } for cc in complexity
                ]
            }
            return results
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Radon: {str(e)}")
            return {'error': str(e)}

    def run_vulture_analysis(self, code: str) -> Dict:
        """
        Détecte le code mort avec Vulture.

        Args:
            code (str): Le code source à analyser

        Returns:
            Dict: Résultats de l'analyse contenant :
                - unused_vars: Variables non utilisées
                - unused_funcs: Fonctions non utilisées
                - error: Message d'erreur en cas de problème
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            v = vulture.Vulture()
            v.scavenge([temp_path])

            return {
                'unused_vars': [
                    {
                        'name': item.name,
                        'type': 'variable',
                        'line': item.first_lineno,
                        'size': item.size
                    }
                    for item in v.unused_vars
                ],
                'unused_funcs': [
                    {
                        'name': item.name,
                        'type': 'function',
                        'line': item.first_lineno,
                        'size': item.size
                    }
                    for item in v.unused_funcs
                ]
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Vulture: {str(e)}")
            return {'error': str(e)}
        finally:
            if 'temp_path' in locals():
                os.unlink(temp_path)

    def run_prospector_analysis(self, code: str) -> Dict:
        """
        Analyse la qualité du code avec Prospector.

        Args:
            code (str): Le code source à analyser

        Returns:
            Dict: Résultats de l'analyse contenant :
                - messages: Liste des problèmes de qualité
                - error: Message d'erreur en cas de problème
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            # Configuration Prospector
            from prospector.config import ProspectorConfig
            from prospector.run import Prospector
            
            config = ProspectorConfig()
            prospector = Prospector(config)
            prospector.execute()

            return {
                'messages': [
                    {
                        'type': msg.source,
                        'message': msg.message,
                        'line': getattr(msg, 'line', 'N/A'),
                        'character': getattr(msg, 'character', 'N/A')
                    }
                    for msg in prospector.get_messages()
                ]
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Prospector: {str(e)}")
            return {'error': str(e)}
        finally:
            if 'temp_path' in locals():
                os.unlink(temp_path)

    def run_flake8_analysis(self, code: str) -> Dict:
        """
        Analyse le code avec flake8.
        
        Args:
            code: Le code source à analyser
            
        Returns:
            Dict: Résultats de l'analyse contenant :
                - messages: Liste des problèmes trouvés
                - error: Message d'erreur en cas de problème
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            try:
                from flake8.api import legacy as flake8
                
                style_guide = flake8.get_style_guide(
                    max_line_length=100,
                    max_complexity=10,
                    ignore=['E203', 'W503']
                )
                
                report = style_guide.check_files([temp_path])
                
                return {
                    'messages': [
                        {
                            'type': 'style',
                            'code': error[1],
                            'message': error[2],
                            'line': error[0],
                            'column': error[3]
                        }
                        for error in report.get_statistics('')
                    ]
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse flake8 : {str(e)}")
                return {'error': str(e), 'messages': []}
                
        finally:
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def analyze(self, code: str, filename: str = "code.py") -> Dict[str, Any]:
        """Analyse complète du code source."""
        from AuditronAI.app.ui_manager import UIManager
        ui = UIManager()
        try:
            # Configuration de l'interface
            ui.setup_ui()
            
            # Initialisation sans thread de conseils
            ui.update_status("🔍 Préparation de l'analyse...")
            ui.update_progress(10)
            
            # Initialiser les résultats
            results = self._get_default_results()
            results['file'] = filename
            
            try:
                # Bandit (25%)
                ui.update_status("🔍 Analyse des vulnérabilités avec Bandit...")
                bandit_results = self.run_bandit_analysis(code, filename)
                if isinstance(bandit_results, dict) and not bandit_results.get('error'):
                    results['security_issues'] = bandit_results.get('issues', [])
                ui.update_progress(25)
                
                # Radon (50%)
                ui.update_status("📊 Analyse de la complexité avec Radon...")
                radon_results = self.run_radon_analysis(code)
                if not radon_results.get('error'):
                    results['code_quality'].update({
                        'complexity': radon_results.get('average_complexity', 0),
                        'functions': radon_results.get('functions', [])
                    })
                ui.update_progress(50)
                
                # Vulture (75%)
                ui.update_status("🧹 Détection du code mort avec Vulture...")
                vulture_results = self.run_vulture_analysis(code)
                if not vulture_results.get('error'):
                    results['code_quality']['unused_code'] = {
                        'variables': vulture_results.get('unused_vars', []),
                        'functions': vulture_results.get('unused_funcs', [])
                    }
                ui.update_progress(75)
                
                # Flake8 (85%)
                ui.update_status("🔍 Analyse du style avec Flake8...")
                flake8_results = self.run_flake8_analysis(code)
                if not flake8_results.get('error'):
                    results['code_quality']['style_issues'] = flake8_results.get('messages', [])
                ui.update_progress(85)
                
                # Prospector (100%)
                ui.update_status("✨ Analyse de la qualité avec Prospector...")
                prospector_results = self.run_prospector_analysis(code)
                if not prospector_results.get('error'):
                    results['code_quality']['style_issues'].extend(prospector_results.get('messages', []))
                ui.update_progress(100)
                
                # Formater les résultats
                formatted_results = {
                    'file': filename,
                    'explanation': (
                        "### 🔍 Résultats de l'analyse détaillée\n\n"
                        "Cette analyse comprend plusieurs aspects :\n\n"
                        "1. **Sécurité** 🔒\n"
                        "   - Détection des vulnérabilités avec Bandit\n"
                        "   - Analyse des problèmes de sécurité courants\n\n"
                        "2. **Complexité** 📊\n"
                        "   - Mesure de la complexité cyclomatique\n"
                        "   - Identification des fonctions complexes\n\n"
                        "3. **Code mort** 🧹\n"
                        "   - Détection des variables non utilisées\n"
                        "   - Identification du code inutilisé\n\n"
                        "4. **Style** ✨\n"
                        "   - Vérification des bonnes pratiques\n"
                        "   - Analyse de la qualité du code\n\n"
                    ),
                    'security_issues': results['security_issues'],
                    'code_quality': results['code_quality'],
                    'summary': self._calculate_summary(results)
                }
                
                return formatted_results
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse : {str(e)}")
                return self._get_default_results()
            
        finally:
            ui.cleanup()
    
    def _get_default_results(self):
        """Retourne une structure de résultats par défaut en cas d'erreur."""
        return {
            'file': 'error.py',
            'security_issues': [],
            'code_quality': {
                'complexity': 0,
                'functions': [],
                'unused_code': {'variables': [], 'functions': []},
                'style_issues': []
            },
            'summary': {
                'severity_counts': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'total_issues': 0,
                'score': 0.0,
                'details': "Erreur lors de l'analyse"
            }
        }
    
    def _calculate_summary(self, results: Dict) -> Dict:
        """Calcule le résumé des résultats."""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        # Compter les problèmes par sévérité
        for issue in results['security_issues']:
            severity = issue.get('severity', '').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Log pour debug
        logger.debug(f"Severity counts calculés : {severity_counts}")
        
        # Calculer le score en fonction des seuils configurés
        total_issues = sum(severity_counts.values())
        score = 100.0
        
        # Pénalités basées sur les seuils
        penalties = {
            'critical': 20 if severity_counts['critical'] > self.severity_thresholds['critical'] else 0,
            'high': 10 if severity_counts['high'] > self.severity_thresholds['high'] else 0,
            'medium': 5 if severity_counts['medium'] > self.severity_thresholds['medium'] else 0,
            'low': 1 if severity_counts['low'] > self.severity_thresholds['low'] else 0
        }
        
        # Appliquer les pénalités
        for severity, count in severity_counts.items():
            if count > 0:
                score -= penalties[severity] * count
        
        # Pénalité pour complexité excessive
        avg_complexity = results['code_quality'].get('complexity', 0)
        if avg_complexity > self.max_complexity:
            score -= (avg_complexity - self.max_complexity) * 2
        
        return {
            'severity_counts': severity_counts,
            'total_issues': total_issues,
            'score': max(0.0, min(100.0, score)),
            'details': self._generate_summary_details(severity_counts, avg_complexity)
        }
    
    def _generate_summary_details(self, severity_counts: Dict[str, int], complexity: float) -> str:
        """Génère les détails du résumé."""
        details = []
        
        # Ajouter les problèmes de sécurité
        for severity, count in severity_counts.items():
            if count > 0:
                threshold = self.severity_thresholds[severity]
                if count > threshold:
                    details.append(f"⚠️ {count} problème(s) de sévérité {severity.upper()} (seuil: {threshold})")
        
        # Ajouter la complexité
        if complexity > self.max_complexity:
            details.append(f"⚠️ Complexité ({complexity:.1f}) supérieure au seuil ({self.max_complexity})")
        
        if not details:
            return "✅ Aucun problème majeur détecté"
        
        return "\n".join(details)
    