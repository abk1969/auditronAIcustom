"""Analyseur de qualité du code."""
import ast
import re
from typing import Dict, List, Any
from collections import defaultdict

class CodeQualityAnalyzer:
    """Analyseur de qualité du code."""
    
    def __init__(self):
        """Initialise l'analyseur."""
        self.issues = []
        self.metrics = {}
        self.current_file = ""
        
    def analyze(self, code: str, filename: str) -> Dict[str, Any]:
        """Analyse la qualité du code.
        
        Args:
            code: Code à analyser
            filename: Nom du fichier
            
        Returns:
            Résultats de l'analyse
        """
        self.current_file = filename
        self.issues = []
        self.metrics = {}
        
        try:
            tree = ast.parse(code)
            
            # Analyse de la complexité
            self._analyze_complexity(tree)
            
            # Analyse des duplications
            self._analyze_duplications(code)
            
            # Analyse du style PEP8
            self._analyze_style(code)
            
            # Analyse de la maintenabilité
            self._analyze_maintainability(tree, code)
            
            return {
                "issues": self.issues,
                "metrics": self.metrics,
                "quality_score": self._calculate_quality_score()
            }
            
        except Exception as e:
            return {
                "issues": [{
                    "type": "analysis_error",
                    "message": str(e),
                    "severity": 1.0,
                    "line": 0
                }],
                "metrics": {},
                "quality_score": 0.0
            }

    def _analyze_complexity(self, tree: ast.AST) -> None:
        """Analyse la complexité cyclomatique."""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                
            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_ExceptHandler(self, node):
                self.complexity += 1
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                local_visitor = ComplexityVisitor()
                local_visitor.generic_visit(node)
                if local_visitor.complexity > 10:  # Seuil de complexité
                    self.complexity += local_visitor.complexity
                
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        self.metrics['complexity'] = visitor.complexity
        if visitor.complexity > 20:  # Seuil global
            self.issues.append({
                "type": "high_complexity",
                "message": f"Complexité cyclomatique trop élevée ({visitor.complexity})",
                "severity": 0.7,
                "line": 0
            })

    def _analyze_duplications(self, code: str) -> None:
        """Analyse les duplications de code."""
        lines = code.split('\n')
        block_size = 6  # Taille minimale d'un bloc dupliqué
        blocks = defaultdict(list)
        
        for i in range(len(lines) - block_size + 1):
            block = '\n'.join(lines[i:i + block_size])
            if len(block.strip()) > 0:  # Ignorer les blocs vides
                blocks[block].append(i + 1)
        
        duplications = {block: lines for block, lines in blocks.items() if len(lines) > 1}
        self.metrics['duplications'] = len(duplications)
        
        for block, line_numbers in duplications.items():
            self.issues.append({
                "type": "code_duplication",
                "message": f"Code dupliqué trouvé aux lignes {', '.join(map(str, line_numbers))}",
                "severity": 0.5,
                "line": line_numbers[0]
            })

    def _analyze_style(self, code: str) -> None:
        """Analyse le style selon PEP8."""
        lines = code.split('\n')
        
        # Vérification de la longueur des lignes
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                self.issues.append({
                    "type": "line_length",
                    "message": "Ligne trop longue (>79 caractères)",
                    "severity": 0.3,
                    "line": i
                })
        
        # Vérification des noms de variables
        snake_case_pattern = re.compile(r'^[a-z_][a-z0-9_]*$')
        class NameChecker(ast.NodeVisitor):
            def __init__(self, issues):
                self.issues = issues
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store) and not snake_case_pattern.match(node.id):
                    self.issues.append({
                        "type": "naming_convention",
                        "message": f"Le nom '{node.id}' ne suit pas la convention snake_case",
                        "severity": 0.3,
                        "line": node.lineno
                    })
                
        checker = NameChecker(self.issues)
        checker.visit(ast.parse(code))

    def _analyze_maintainability(self, tree: ast.AST, code: str) -> None:
        """Analyse la maintenabilité du code."""
        # Taille des fonctions
        class FunctionAnalyzer(ast.NodeVisitor):
            def __init__(self, issues):
                self.issues = issues
                
            def visit_FunctionDef(self, node):
                end_lineno = max(child.lineno for child in ast.walk(node))
                size = end_lineno - node.lineno
                
                if size > 50:  # Seuil arbitraire
                    self.issues.append({
                        "type": "function_size",
                        "message": f"Fonction {node.name} trop longue ({size} lignes)",
                        "severity": 0.6,
                        "line": node.lineno
                    })
                    
                # Vérifier le nombre de paramètres
                if len(node.args.args) > 5:  # Seuil arbitraire
                    self.issues.append({
                        "type": "too_many_arguments",
                        "message": f"Trop de paramètres dans la fonction {node.name}",
                        "severity": 0.4,
                        "line": node.lineno
                    })
                
        analyzer = FunctionAnalyzer(self.issues)
        analyzer.visit(tree)
        
        # Ratio commentaires/code
        comments = len([l for l in code.split('\n') if l.strip().startswith('#')])
        total_lines = len(code.split('\n'))
        comment_ratio = comments / total_lines if total_lines > 0 else 0
        
        self.metrics['comment_ratio'] = round(comment_ratio, 2)
        if comment_ratio < 0.1:  # Seuil arbitraire
            self.issues.append({
                "type": "low_comments",
                "message": "Ratio de commentaires trop faible",
                "severity": 0.4,
                "line": 0
            })

    def _calculate_quality_score(self) -> float:
        """Calcule le score de qualité global.
        
        Returns:
            Score entre 0 et 1
        """
        if not self.issues:
            return 1.0
            
        # Pondération des problèmes par sévérité
        total_severity = sum(issue['severity'] for issue in self.issues)
        base_score = max(0.0, 1.0 - (total_severity / len(self.issues)))
        
        # Ajustement basé sur les métriques
        complexity_penalty = min(0.3, self.metrics.get('complexity', 0) / 100)
        duplication_penalty = min(0.3, self.metrics.get('duplications', 0) / 10)
        
        final_score = base_score - complexity_penalty - duplication_penalty
        return round(max(0.0, min(1.0, final_score)), 2)
