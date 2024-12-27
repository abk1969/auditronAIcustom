"""Analyseur de sécurité pour SQL."""
import re
import sqlparse
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from .interfaces import AnalyzerType
from ..logger import logger
from ..error_handling import SecurityError, ErrorSeverity

class SQLAnalyzer(BaseAnalyzer):
    """Analyseur de sécurité spécialisé pour SQL."""

    @property
    def analyzer_type(self) -> AnalyzerType:
        """Retourne le type d'analyseur."""
        return AnalyzerType.SQL

    async def _setup(self) -> None:
        """Configure l'analyseur."""
        self.dangerous_patterns = {
            r'\bUNION\b.*\bSELECT\b': {
                'type': 'sql_injection',
                'description': 'Possible injection SQL via UNION SELECT',
                'severity': 'critical',
                'cwe': ['CWE-89']
            },
            r'--.*$': {
                'type': 'sql_comment',
                'description': 'Commentaire SQL suspect',
                'severity': 'medium',
                'cwe': ['CWE-89']
            },
            r'/\*.*?\*/': {
                'type': 'sql_comment',
                'description': 'Commentaire SQL multi-ligne suspect',
                'severity': 'medium',
                'cwe': ['CWE-89']
            },
            r'\bOR\b.*?[\'"].*?[\'"].*?=': {
                'type': 'sql_injection',
                'description': 'Possible injection SQL via OR condition',
                'severity': 'critical',
                'cwe': ['CWE-89']
            },
            r'\bEXEC\b.*?\(': {
                'type': 'sql_execution',
                'description': 'Exécution dynamique de SQL',
                'severity': 'high',
                'cwe': ['CWE-89']
            },
            r'\bINTO\b.*?\bOUTFILE\b': {
                'type': 'file_operation',
                'description': 'Écriture de fichier via SQL',
                'severity': 'high',
                'cwe': ['CWE-89']
            },
            r'\bLOAD_FILE\b': {
                'type': 'file_operation',
                'description': 'Lecture de fichier via SQL',
                'severity': 'high',
                'cwe': ['CWE-89']
            },
            r'\bSYSTEM_USER\b': {
                'type': 'information_disclosure',
                'description': 'Accès aux informations système',
                'severity': 'medium',
                'cwe': ['CWE-200']
            },
            r'\bCONCAT\b.*?\(': {
                'type': 'sql_injection',
                'description': 'Concaténation SQL potentiellement dangereuse',
                'severity': 'medium',
                'cwe': ['CWE-89']
            }
        }
        
        self.best_practices = {
            r'\*': {
                'type': 'performance',
                'description': 'SELECT * déconseillé',
                'severity': 'low',
                'cwe': []
            },
            r'\bLIKE\b.*?[\'"]%': {
                'type': 'performance',
                'description': 'LIKE avec wildcard au début',
                'severity': 'low',
                'cwe': []
            },
            r'\bNOT\b.*\bIN\b': {
                'type': 'performance',
                'description': 'NOT IN peut être lent',
                'severity': 'low',
                'cwe': []
            }
        }

    async def _analyze_impl(self) -> Dict[str, Any]:
        """
        Effectue l'analyse SQL.
        
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Parser le SQL
            statements = sqlparse.parse(self.context.code)
            
            # Analyser chaque statement
            security_issues = []
            for statement in statements:
                # Vérifier les motifs dangereux
                security_issues.extend(
                    self._check_patterns(str(statement), self.dangerous_patterns)
                )
                
                # Vérifier les bonnes pratiques
                security_issues.extend(
                    self._check_patterns(str(statement), self.best_practices)
                )
                
                # Analyses spécifiques par type de statement
                if statement.get_type() == 'SELECT':
                    security_issues.extend(self._analyze_select(statement))
                elif statement.get_type() == 'INSERT':
                    security_issues.extend(self._analyze_insert(statement))
                elif statement.get_type() == 'UPDATE':
                    security_issues.extend(self._analyze_update(statement))
                elif statement.get_type() == 'DELETE':
                    security_issues.extend(self._analyze_delete(statement))
                
            return {
                'security_issues': security_issues
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse SQL: {str(e)}")
            raise SecurityError(
                message=f"Erreur lors de l'analyse SQL: {str(e)}",
                vulnerability_type="sql_analysis_error",
                severity=ErrorSeverity.ERROR
            )

    def _check_patterns(
        self,
        sql: str,
        patterns: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Vérifie les motifs dans le SQL.
        
        Args:
            sql: Code SQL à analyser
            patterns: Motifs à rechercher
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        for pattern, info in patterns.items():
            matches = re.finditer(pattern, sql, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': info['type'],
                    'description': info['description'],
                    'severity': info['severity'],
                    'line_number': sql[:match.start()].count('\n') + 1,
                    'code': match.group(),
                    'cwe': info['cwe']
                })
        return issues

    def _analyze_select(self, statement: sqlparse.sql.Statement) -> List[Dict[str, Any]]:
        """
        Analyse une requête SELECT.
        
        Args:
            statement: Requête à analyser
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        
        # Vérifier WHERE clause
        where_found = False
        for token in statement.tokens:
            if token.is_keyword and token.value.upper() == 'WHERE':
                where_found = True
                break
                
        if not where_found:
            issues.append({
                'type': 'sql_best_practice',
                'description': 'SELECT sans clause WHERE',
                'severity': 'medium',
                'line_number': statement.tokens[0].lineno,
                'code': str(statement),
                'cwe': []
            })
            
        # Vérifier ORDER BY sans LIMIT
        if (
            any(t.is_keyword and t.value.upper() == 'ORDER' for t in statement.tokens) and
            not any(t.is_keyword and t.value.upper() == 'LIMIT' for t in statement.tokens)
        ):
            issues.append({
                'type': 'sql_best_practice',
                'description': 'ORDER BY sans LIMIT',
                'severity': 'low',
                'line_number': statement.tokens[0].lineno,
                'code': str(statement),
                'cwe': []
            })
            
        return issues

    def _analyze_insert(self, statement: sqlparse.sql.Statement) -> List[Dict[str, Any]]:
        """
        Analyse une requête INSERT.
        
        Args:
            statement: Requête à analyser
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        
        # Vérifier les colonnes explicites
        values_token = None
        for token in statement.tokens:
            if token.is_keyword and token.value.upper() == 'VALUES':
                values_token = token
                break
                
        if values_token and not any(
            t.is_group and '(' in str(t)
            for t in statement.tokens[:statement.token_index(values_token)]
        ):
            issues.append({
                'type': 'sql_best_practice',
                'description': 'INSERT sans liste de colonnes explicite',
                'severity': 'medium',
                'line_number': statement.tokens[0].lineno,
                'code': str(statement),
                'cwe': []
            })
            
        return issues

    def _analyze_update(self, statement: sqlparse.sql.Statement) -> List[Dict[str, Any]]:
        """
        Analyse une requête UPDATE.
        
        Args:
            statement: Requête à analyser
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        
        # Vérifier WHERE clause
        where_found = False
        for token in statement.tokens:
            if token.is_keyword and token.value.upper() == 'WHERE':
                where_found = True
                break
                
        if not where_found:
            issues.append({
                'type': 'sql_security',
                'description': 'UPDATE sans clause WHERE',
                'severity': 'high',
                'line_number': statement.tokens[0].lineno,
                'code': str(statement),
                'cwe': ['CWE-89']
            })
            
        return issues

    def _analyze_delete(self, statement: sqlparse.sql.Statement) -> List[Dict[str, Any]]:
        """
        Analyse une requête DELETE.
        
        Args:
            statement: Requête à analyser
            
        Returns:
            Liste des problèmes trouvés
        """
        issues = []
        
        # Vérifier WHERE clause
        where_found = False
        for token in statement.tokens:
            if token.is_keyword and token.value.upper() == 'WHERE':
                where_found = True
                break
                
        if not where_found:
            issues.append({
                'type': 'sql_security',
                'description': 'DELETE sans clause WHERE',
                'severity': 'high',
                'line_number': statement.tokens[0].lineno,
                'code': str(statement),
                'cwe': ['CWE-89']
            })
            
        return issues

    def _get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """
        Génère une suggestion de correction.
        
        Args:
            issue: Problème à corriger
            
        Returns:
            Suggestion de correction
        """
        issue_type = issue['type']
        
        if issue_type == 'sql_injection':
            return "Utiliser des requêtes préparées avec des paramètres liés"
        elif issue_type == 'sql_comment':
            return "Éviter les commentaires dans les requêtes SQL"
        elif issue_type == 'sql_execution':
            return "Éviter l'exécution dynamique de SQL"
        elif issue_type == 'file_operation':
            return "Ne pas utiliser SQL pour les opérations sur les fichiers"
        elif issue_type == 'information_disclosure':
            return "Limiter l'accès aux informations sensibles"
        elif issue_type == 'performance':
            if 'SELECT *' in issue['code']:
                return "Spécifier explicitement les colonnes nécessaires"
            elif 'LIKE' in issue['code']:
                return "Éviter les wildcards au début des patterns LIKE"
            elif 'NOT IN' in issue['code']:
                return "Utiliser NOT EXISTS ou LEFT JOIN"
        elif issue_type == 'sql_best_practice':
            if 'WHERE' in issue['description']:
                return "Ajouter une clause WHERE appropriée"
            elif 'ORDER BY' in issue['description']:
                return "Ajouter LIMIT pour limiter les résultats"
            elif 'INSERT' in issue['description']:
                return "Spécifier explicitement les colonnes dans l'INSERT"
                
        return "Revoir la requête SQL pour plus de sécurité"
