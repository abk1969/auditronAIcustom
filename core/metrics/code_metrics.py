"""Collecte et analyse des métriques de code."""
from typing import Dict, Any, List, Optional, NamedTuple
from dataclasses import dataclass
import ast
import re
from pathlib import Path

@dataclass
class FunctionMetrics:
    """Métriques pour une fonction."""
    name: str
    lines: int
    complexity: int
    parameters: int
    returns: int
    cognitive_complexity: int
    nested_depth: int
    statements: int
    docstring: Optional[str]
    start_line: int
    end_line: int

@dataclass
class ClassMetrics:
    """Métriques pour une classe."""
    name: str
    methods: List[FunctionMetrics]
    lines: int
    complexity: int
    inheritance_depth: int
    attributes: int
    docstring: Optional[str]
    start_line: int
    end_line: int

class ModuleMetrics:
    """Collecteur de métriques pour un module."""

    def __init__(self, code: str, filename: str = "<unknown>"):
        """
        Initialise le collecteur de métriques.
        
        Args:
            code: Code source à analyser
            filename: Nom du fichier
        """
        self.code = code
        self.filename = filename
        self.tree = ast.parse(code)
        self._current_class: Optional[str] = None
        self._metrics: Dict[str, Any] = {
            'functions': [],
            'classes': [],
            'imports': [],
            'lines': len(code.splitlines()),
            'complexity': 0,
            'maintainability_index': 0.0,
            'loc': self._count_lines_of_code(),
            'comments': self._count_comments(),
            'cognitive_complexity': 0
        }
        self._analyze()

    def _count_lines_of_code(self) -> int:
        """Compte les lignes de code effectives."""
        lines = self.code.splitlines()
        non_empty_lines = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith('#')
        ]
        return len(non_empty_lines)

    def _count_comments(self) -> int:
        """Compte les lignes de commentaires."""
        lines = self.code.splitlines()
        comment_lines = [
            line.strip()
            for line in lines
            if line.strip().startswith('#')
        ]
        return len(comment_lines)

    def _analyze(self) -> None:
        """Analyse le code source."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node)
            elif isinstance(node, ast.Import):
                self._analyze_import(node)
            elif isinstance(node, ast.ImportFrom):
                self._analyze_import_from(node)

        # Calculer la complexité cognitive globale
        self._metrics['cognitive_complexity'] = sum(
            func.cognitive_complexity
            for func in self._metrics['functions']
        )

        # Calculer l'indice de maintenabilité
        self._calculate_maintainability_index()

    def _analyze_function(self, node: ast.FunctionDef) -> None:
        """
        Analyse une fonction.
        
        Args:
            node: Nœud AST de la fonction
        """
        metrics = FunctionMetrics(
            name=node.name,
            lines=len(node.body),
            complexity=self._calculate_complexity(node),
            parameters=len(node.args.args),
            returns=self._count_returns(node),
            cognitive_complexity=self._calculate_cognitive_complexity(node),
            nested_depth=self._calculate_nested_depth(node),
            statements=self._count_statements(node),
            docstring=ast.get_docstring(node),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno
        )

        if self._current_class:
            # Ajouter aux méthodes de la classe courante
            for class_metrics in self._metrics['classes']:
                if class_metrics.name == self._current_class:
                    class_metrics.methods.append(metrics)
                    break
        else:
            # Ajouter aux fonctions du module
            self._metrics['functions'].append(metrics)

    def _analyze_class(self, node: ast.ClassDef) -> None:
        """
        Analyse une classe.
        
        Args:
            node: Nœud AST de la classe
        """
        self._current_class = node.name
        
        metrics = ClassMetrics(
            name=node.name,
            methods=[],
            lines=len(node.body),
            complexity=self._calculate_complexity(node),
            inheritance_depth=len(node.bases),
            attributes=self._count_attributes(node),
            docstring=ast.get_docstring(node),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno
        )
        
        # Analyser les méthodes
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self._analyze_function(child)
        
        self._metrics['classes'].append(metrics)
        self._current_class = None

    def _analyze_import(self, node: ast.Import) -> None:
        """
        Analyse une instruction import.
        
        Args:
            node: Nœud AST de l'import
        """
        for name in node.names:
            self._metrics['imports'].append({
                'name': name.name,
                'asname': name.asname,
                'line': node.lineno
            })

    def _analyze_import_from(self, node: ast.ImportFrom) -> None:
        """
        Analyse une instruction import from.
        
        Args:
            node: Nœud AST de l'import from
        """
        module = node.module or ''
        for name in node.names:
            self._metrics['imports'].append({
                'module': module,
                'name': name.name,
                'asname': name.asname,
                'line': node.lineno
            })

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calcule la complexité cyclomatique.
        
        Args:
            node: Nœud AST à analyser
            
        Returns:
            Complexité calculée
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try,
                               ast.ExceptHandler, ast.With,
                               ast.Assert, ast.Raise)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """
        Calcule la complexité cognitive.
        
        Args:
            node: Nœud AST à analyser
            
        Returns:
            Complexité cognitive calculée
        """
        complexity = 0
        nesting_level = 0

        class CognitiveComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0

            def visit_If(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_While(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_For(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_Try(self, node):
                self.complexity += (1 + self.nesting_level)
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

        visitor = CognitiveComplexityVisitor()
        visitor.visit(node)
        return visitor.complexity

    def _calculate_nested_depth(self, node: ast.AST) -> int:
        """
        Calcule la profondeur d'imbrication maximale.
        
        Args:
            node: Nœud AST à analyser
            
        Returns:
            Profondeur maximale
        """
        max_depth = 0
        current_depth = 0

        class DepthVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_depth = 0
                self.current_depth = 0

            def visit_If(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1

            def visit_For(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1

            def visit_While(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1

            def visit_Try(self, node):
                self.current_depth += 1
                self.max_depth = max(self.max_depth, self.current_depth)
                self.generic_visit(node)
                self.current_depth -= 1

        visitor = DepthVisitor()
        visitor.visit(node)
        return visitor.max_depth

    def _count_statements(self, node: ast.AST) -> int:
        """
        Compte le nombre d'instructions.
        
        Args:
            node: Nœud AST à analyser
            
        Returns:
            Nombre d'instructions
        """
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.Return,
                               ast.Raise, ast.Assert, ast.Pass, ast.Break,
                               ast.Continue, ast.Import, ast.ImportFrom,
                               ast.Expr, ast.Delete)):
                count += 1
        return count

    def _count_returns(self, node: ast.AST) -> int:
        """
        Compte le nombre de return statements.
        
        Args:
            node: Nœud AST à analyser
            
        Returns:
            Nombre de returns
        """
        return len([n for n in ast.walk(node) if isinstance(n, ast.Return)])

    def _count_attributes(self, node: ast.ClassDef) -> int:
        """
        Compte le nombre d'attributs d'une classe.
        
        Args:
            node: Nœud AST de la classe
            
        Returns:
            Nombre d'attributs
        """
        count = 0
        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                count += 1
            elif isinstance(child, ast.Assign):
                count += len(child.targets)
        return count

    def _calculate_maintainability_index(self) -> None:
        """Calcule l'indice de maintenabilité."""
        # Formule standard de l'indice de maintenabilité
        loc = self._metrics['loc']
        complexity = self._metrics['complexity']
        comments = self._metrics['comments']
        
        if loc > 0:
            comments_ratio = comments / loc
        else:
            comments_ratio = 0
            
        # Calculer l'indice (0-100)
        maintainability = (
            171 -
            (5.2 * complexity) -
            (0.23 * loc) +
            (50 * comments_ratio)
        )
        
        # Normaliser entre 0 et 100
        self._metrics['maintainability_index'] = max(0, min(100, maintainability))

    @property
    def metrics(self) -> Dict[str, Any]:
        """Retourne les métriques collectées."""
        return self._metrics

    def get_complex_functions(self, threshold: int = 10) -> List[FunctionMetrics]:
        """
        Retourne les fonctions dépassant un seuil de complexité.
        
        Args:
            threshold: Seuil de complexité
            
        Returns:
            Liste des fonctions complexes
        """
        complex_funcs = []
        
        # Fonctions du module
        for func in self._metrics['functions']:
            if func.complexity > threshold:
                complex_funcs.append(func)
                
        # Méthodes des classes
        for cls in self._metrics['classes']:
            for method in cls.methods:
                if method.complexity > threshold:
                    complex_funcs.append(method)
                    
        return complex_funcs

    def get_long_functions(self, threshold: int = 50) -> List[FunctionMetrics]:
        """
        Retourne les fonctions dépassant un seuil de lignes.
        
        Args:
            threshold: Seuil de lignes
            
        Returns:
            Liste des fonctions longues
        """
        long_funcs = []
        
        # Fonctions du module
        for func in self._metrics['functions']:
            if func.lines > threshold:
                long_funcs.append(func)
                
        # Méthodes des classes
        for cls in self._metrics['classes']:
            for method in cls.methods:
                if method.lines > threshold:
                    long_funcs.append(method)
                    
        return long_funcs

    def get_deeply_nested_functions(
        self,
        threshold: int = 3
    ) -> List[FunctionMetrics]:
        """
        Retourne les fonctions trop imbriquées.
        
        Args:
            threshold: Seuil d'imbrication
            
        Returns:
            Liste des fonctions imbriquées
        """
        nested_funcs = []
        
        # Fonctions du module
        for func in self._metrics['functions']:
            if func.nested_depth > threshold:
                nested_funcs.append(func)
                
        # Méthodes des classes
        for cls in self._metrics['classes']:
            for method in cls.methods:
                if method.nested_depth > threshold:
                    nested_funcs.append(method)
                    
        return nested_funcs
