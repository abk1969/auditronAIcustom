"""Stratégies d'analyse pour TypeScript."""
from typing import Dict, Any, List
import re
from ..repositories.typescript_patterns import TypeScriptPatternsRepository

class SecurityAnalysisStrategy:
    """Stratégie d'analyse de sécurité pour TypeScript."""

    def __init__(self, patterns_repo: TypeScriptPatternsRepository):
        """Initialise la stratégie avec un repository de patterns."""
        self.patterns_repo = patterns_repo

    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyse le code pour les problèmes de sécurité."""
        security_issues = []
        patterns = self.patterns_repo.get_security_patterns()

        for pattern_name, pattern in patterns.items():
            matches = list(pattern.finditer(code))
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                security_issues.append({
                    'type': pattern_name,
                    'line': line_number,
                    'description': self._get_issue_description(pattern_name),
                    'severity': self._get_severity(pattern_name),
                    'code': code[max(0, match.start()-20):match.end()+20].strip()
                })

        return {
            'security_issues': security_issues,
            'total_issues': len(security_issues)
        }

    def _get_issue_description(self, pattern_name: str) -> str:
        """Retourne la description d'un problème de sécurité."""
        descriptions = {
            'eval_usage': "Utilisation dangereuse de eval(). Risque d'exécution de code malveillant.",
            'function_constructor': "Construction dangereuse de fonction. Risque d'injection de code.",
            'dangerous_innerHTML': "Utilisation non sécurisée de innerHTML. Risque XSS.",
            'sql_injection': "Possible injection SQL. Utiliser des requêtes paramétrées.",
            'command_injection': "Possible injection de commande. Valider les entrées.",
            'sensitive_data': "Données sensibles potentiellement exposées.",
            'insecure_random': "Utilisation de Math.random() pour la sécurité. Utiliser crypto.getRandomValues().",
            'prototype_pollution': "Risque de pollution de prototype. Valider les entrées.",
            'xss_vulnerable': "Point d'entrée XSS potentiel. Échapper les données.",
            'unsafe_regex': "Construction non sécurisée d'expression régulière."
        }
        return descriptions.get(pattern_name, "Problème de sécurité détecté")

    def _get_severity(self, pattern_name: str) -> str:
        """Retourne la sévérité d'un problème de sécurité."""
        high_severity = {'eval_usage', 'sql_injection', 'command_injection', 'xss_vulnerable'}
        medium_severity = {'dangerous_innerHTML', 'sensitive_data', 'prototype_pollution'}
        
        if pattern_name in high_severity:
            return 'HIGH'
        elif pattern_name in medium_severity:
            return 'MEDIUM'
        return 'LOW'

class QualityAnalysisStrategy:
    """Stratégie d'analyse de qualité pour TypeScript."""

    def __init__(self):
        """Initialise la stratégie."""
        self.patterns_repo = TypeScriptPatternsRepository()

    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyse le code pour les problèmes de qualité."""
        quality_issues = []
        patterns = self.patterns_repo.get_quality_patterns()

        for pattern_name, pattern in patterns.items():
            matches = list(pattern.finditer(code))
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                quality_issues.append({
                    'type': pattern_name,
                    'line': line_number,
                    'description': self._get_issue_description(pattern_name),
                    'impact': self._get_impact(pattern_name),
                    'code': code[max(0, match.start()-20):match.end()+20].strip()
                })

        # Analyse supplémentaire de la qualité
        complexity_score = self._calculate_complexity(code)
        maintainability_score = self._calculate_maintainability(code, len(quality_issues))

        return {
            'quality_issues': quality_issues,
            'total_issues': len(quality_issues),
            'complexity_score': complexity_score,
            'maintainability_score': maintainability_score
        }

    def _get_issue_description(self, pattern_name: str) -> str:
        """Retourne la description d'un problème de qualité."""
        descriptions = {
            'console_log': "Console.log laissé dans le code. À retirer en production.",
            'any_type': "Utilisation du type 'any'. Spécifier un type plus précis.",
            'empty_catch': "Bloc catch vide. Gérer ou documenter l'exception.",
            'magic_numbers': "Nombre magique détecté. Utiliser une constante nommée.",
            'long_function': "Fonction trop longue. Diviser en sous-fonctions.",
            'complex_condition': "Condition trop complexe. Simplifier ou extraire.",
            'nested_callbacks': "Callbacks imbriqués. Utiliser async/await.",
            'todo_comment': "TODO trouvé. Planifier la résolution.",
            'unused_import': "Import potentiellement inutilisé.",
            'deprecated_api': "Utilisation d'API dépréciée."
        }
        return descriptions.get(pattern_name, "Problème de qualité détecté")

    def _get_impact(self, pattern_name: str) -> str:
        """Retourne l'impact d'un problème de qualité."""
        high_impact = {'any_type', 'long_function', 'complex_condition'}
        medium_impact = {'empty_catch', 'nested_callbacks', 'deprecated_api'}
        
        if pattern_name in high_impact:
            return 'HIGH'
        elif pattern_name in medium_impact:
            return 'MEDIUM'
        return 'LOW'

    def _calculate_complexity(self, code: str) -> float:
        """Calcule un score de complexité basé sur différents facteurs."""
        # Nombre de structures de contrôle
        control_structures = len(re.findall(r'\b(if|for|while|switch)\b', code))
        # Nombre de fonctions
        functions = len(re.findall(r'\bfunction\b', code))
        # Imbrication maximale
        nesting_level = max([len(line.split('{')) for line in code.split('\n')])
        
        # Score pondéré
        return round((control_structures * 0.3 + functions * 0.2 + nesting_level * 0.5), 2)

    def _calculate_maintainability(self, code: str, issues_count: int) -> float:
        """Calcule un score de maintenabilité."""
        # Longueur du code
        code_length = len(code.split('\n'))
        # Ratio commentaires/code
        comments = len(re.findall(r'//.*$|/\*[\s\S]*?\*/', code, re.MULTILINE))
        comment_ratio = comments / max(code_length, 1)
        
        # Score basé sur plusieurs facteurs
        base_score = 100
        length_penalty = min(code_length / 1000, 30)  # Max 30 points
        issues_penalty = min(issues_count * 2, 40)    # Max 40 points
        comment_bonus = min(comment_ratio * 20, 10)   # Max 10 points bonus
        
        final_score = base_score - length_penalty - issues_penalty + comment_bonus
        return round(max(0, min(100, final_score)), 2)
