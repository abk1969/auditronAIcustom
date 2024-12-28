"""Analyseur de sécurité."""
import ast
from typing import Dict, List, Any
from app.core.logger import logger

class SecurityAnalyzer:
    """Analyseur de sécurité du code."""
    
    def __init__(self):
        """Initialise l'analyseur."""
        self.issues = []
        self.current_file = ""
    
    def analyze(self, code: str, filename: str) -> Dict[str, Any]:
        """Analyse le code pour trouver des problèmes de sécurité.
        
        Args:
            code: Code à analyser
            filename: Nom du fichier
            
        Returns:
            Résultats de l'analyse
        """
        self.current_file = filename
        self.issues = []
        
        try:
            tree = ast.parse(code)
            self.visit(tree)
            
            return {
                "issues": self.issues,
                "score": self._calculate_security_score()
            }
            
        except SyntaxError as e:
            logger.error(f"Erreur de syntaxe dans {filename}: {str(e)}")
            return {
                "issues": [{
                    "type": "syntax_error",
                    "message": str(e),
                    "severity": 1.0,
                    "line": e.lineno or 0
                }],
                "score": 0.0
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sécurité de {filename}: {str(e)}")
            return {
                "issues": [],
                "score": 0.0
            }
    
    def visit(self, node: ast.AST) -> None:
        """Visite l'arbre AST pour trouver des problèmes.
        
        Args:
            node: Nœud AST
        """
        # Vérifier les appels système dangereux
        if isinstance(node, ast.Call):
            self._check_dangerous_call(node)
        
        # Vérifier les imports dangereux
        elif isinstance(node, ast.Import):
            self._check_dangerous_import(node)
        
        # Vérifier les assignations de variables sensibles
        elif isinstance(node, ast.Assign):
            self._check_sensitive_assignment(node)
        
        # Visiter récursivement
        for child in ast.iter_child_nodes(node):
            self.visit(child)
    
    def _check_dangerous_call(self, node: ast.Call) -> None:
        """Vérifie les appels de fonction dangereux."""
        dangerous_functions = {
            'os.system': 'Appel système direct',
            'subprocess.run': 'Exécution de processus',
            'eval': 'Évaluation dynamique de code',
            'exec': 'Exécution dynamique de code'
        }
        
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
        
        if func_name in dangerous_functions:
            self.issues.append({
                "type": "dangerous_call",
                "message": f"Utilisation dangereuse de {func_name}: {dangerous_functions[func_name]}",
                "severity": 0.8,
                "line": node.lineno
            })
    
    def _check_dangerous_import(self, node: ast.Import) -> None:
        """Vérifie les imports potentiellement dangereux."""
        dangerous_imports = {
            'subprocess': 'Module d\'exécution de processus',
            'pickle': 'Désérialisation non sécurisée',
            'marshal': 'Désérialisation non sécurisée'
        }
        
        for alias in node.names:
            if alias.name in dangerous_imports:
                self.issues.append({
                    "type": "dangerous_import",
                    "message": f"Import potentiellement dangereux: {alias.name} - {dangerous_imports[alias.name]}",
                    "severity": 0.6,
                    "line": node.lineno
                })
    
    def _check_sensitive_assignment(self, node: ast.Assign) -> None:
        """Vérifie les assignations de variables sensibles."""
        sensitive_patterns = [
            'password',
            'secret',
            'key',
            'token',
            'credential'
        ]
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if any(pattern in name for pattern in sensitive_patterns):
                    # Vérifier si c'est une chaîne en dur
                    if isinstance(node.value, ast.Str):
                        self.issues.append({
                            "type": "hardcoded_secret",
                            "message": f"Variable sensible {target.id} assignée en dur",
                            "severity": 0.9,
                            "line": node.lineno
                        })
    
    def _calculate_security_score(self) -> float:
        """Calcule le score de sécurité basé sur les problèmes trouvés.
        
        Returns:
            Score entre 0 et 1
        """
        if not self.issues:
            return 1.0
            
        # Le score diminue avec chaque problème, pondéré par sa sévérité
        total_severity = sum(issue['severity'] for issue in self.issues)
        score = max(0.0, 1.0 - (total_severity / len(self.issues)))
        
        return round(score, 2)
