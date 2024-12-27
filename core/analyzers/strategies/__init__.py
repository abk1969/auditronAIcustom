"""Module contenant les stratégies d'analyse."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AnalysisStrategy(ABC):
    """Classe abstraite pour les stratégies d'analyse."""
    
    @abstractmethod
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyse le code selon la stratégie."""
        pass

class SecurityAnalysisStrategy(AnalysisStrategy):
    """Stratégie pour l'analyse de sécurité."""
    
    def __init__(self, patterns_repository):
        self.patterns_repository = patterns_repository
        
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyse les problèmes de sécurité dans le code."""
        issues = []
        patterns = self.patterns_repository.get_patterns()
        
        for check_name, check_info in patterns.items():
            matches = check_info['pattern'].finditer(code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    'line': line_number,
                    'description': check_info['description'],
                    'severity': check_info['severity'],
                    'cwe': check_info['cwe'],
                    'code': code.split('\n')[line_number - 1].strip()
                })
                
        return {'security_issues': issues}

class QualityAnalysisStrategy(AnalysisStrategy):
    """Stratégie pour l'analyse de la qualité du code."""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyse la qualité du code."""
        return {
            'code_quality': {
                'complexity': self._calculate_complexity(code),
                'functions': self._find_functions(code),
                'unused_code': self._find_unused_code(code)
            }
        }
        
    def _calculate_complexity(self, code: str) -> float:
        """Calcule la complexité cyclomatique."""
        import re
        control_structures = len(re.findall(r'\b(if|while|for|switch|catch)\b', code))
        logical_operators = len(re.findall(r'(\&\&|\|\|)', code))
        return (control_structures + logical_operators) / max(1, len(code.split('\n')))
        
    def _find_functions(self, code: str) -> List[Dict[str, Any]]:
        """Identifie les fonctions."""
        import re
        functions = []
        function_pattern = r'(?:function\s+(\w+)|(\w+)\s*=\s*function|\(\s*\)\s*=>)'
        matches = re.finditer(function_pattern, code)
        
        for match in matches:
            line_number = code[:match.start()].count('\n') + 1
            name = match.group(1) or match.group(2) or '<anonymous>'
            functions.append({
                'name': name,
                'line': line_number,
                'type': 'function'
            })
            
        return functions
        
    def _find_unused_code(self, code: str) -> Dict[str, List[Dict[str, Any]]]:
        """Détecte le code inutilisé."""
        import re
        unused = {
            'variables': [],
            'functions': [],
            'imports': []
        }

        # Variables
        var_pattern = r'\b(?:let|const|var)\s+(\w+)\s*(?::\s*\w+)?\s*='
        for match in re.finditer(var_pattern, code):
            var_name = match.group(1)
            if len(re.findall(rf'\b{var_name}\b', code)) == 1:
                line_number = code[:match.start()].count('\n') + 1
                unused['variables'].append({
                    'name': var_name,
                    'line': line_number,
                    'type': 'variable'
                })

        # Fonctions
        for func in self._find_functions(code):
            if func['name'] != '<anonymous>' and len(re.findall(rf'\b{func["name"]}\b', code)) == 1:
                unused['functions'].append(func)

        # Imports
        import_pattern = r'import\s+{\s*([^}]+)\s*}'
        for match in re.finditer(import_pattern, code):
            imports = [imp.strip() for imp in match.group(1).split(',')]
            for imp in imports:
                if len(re.findall(rf'\b{imp}\b', code)) == 1:
                    line_number = code[:match.start()].count('\n') + 1
                    unused['imports'].append({
                        'name': imp,
                        'line': line_number,
                        'type': 'import'
                    })

        return unused
