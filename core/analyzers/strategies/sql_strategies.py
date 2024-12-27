"""Stratégies d'analyse pour le code SQL."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class SQLAnalysisStrategy(ABC):
    """Classe de base pour les stratégies d'analyse SQL."""
    
    @abstractmethod
    def analyze(self, sql_code: str) -> Dict[str, Any]:
        """Analyse le code SQL selon la stratégie."""
        pass

class SQLSecurityStrategy(SQLAnalysisStrategy):
    """Stratégie pour l'analyse de sécurité SQL."""
    
    def analyze(self, sql_code: str) -> Dict[str, Any]:
        """
        Analyse les problèmes de sécurité dans le code SQL.
        
        Args:
            sql_code: Code SQL à analyser
            
        Returns:
            Dict contenant les résultats de l'analyse de sécurité
        """
        issues = []
        
        # Vérifie les injections SQL potentielles
        if "EXECUTE" in sql_code.upper() or "EXEC" in sql_code.upper():
            issues.append({
                "type": "security",
                "severity": "high",
                "message": "Utilisation potentiellement dangereuse de EXECUTE/EXEC"
            })
            
        # Vérifie les accès privilégiés
        if "GRANT" in sql_code.upper() or "SUPER" in sql_code.upper():
            issues.append({
                "type": "security",
                "severity": "medium",
                "message": "Opération privilégiée détectée"
            })
            
        return {
            "security_issues": issues,
            "risk_level": "high" if issues else "low"
        }

class SQLPerformanceStrategy(SQLAnalysisStrategy):
    """Stratégie pour l'analyse des performances SQL."""
    
    def analyze(self, sql_code: str) -> Dict[str, Any]:
        """
        Analyse les problèmes de performance dans le code SQL.
        
        Args:
            sql_code: Code SQL à analyser
            
        Returns:
            Dict contenant les résultats de l'analyse de performance
        """
        issues = []
        
        # Vérifie les SELECT *
        if "SELECT *" in sql_code.upper():
            issues.append({
                "type": "performance",
                "severity": "medium",
                "message": "Utilisation de SELECT * peut impacter les performances"
            })
            
        # Vérifie les jointures sans condition
        if "JOIN" in sql_code.upper() and "ON" not in sql_code.upper():
            issues.append({
                "type": "performance",
                "severity": "high",
                "message": "Jointure sans condition détectée"
            })
            
        return {
            "performance_issues": issues,
            "optimization_needed": len(issues) > 0
        }

class SQLQualityStrategy(SQLAnalysisStrategy):
    """Stratégie pour l'analyse de la qualité du code SQL."""
    
    def analyze(self, sql_code: str) -> Dict[str, Any]:
        """
        Analyse la qualité du code SQL.
        
        Args:
            sql_code: Code SQL à analyser
            
        Returns:
            Dict contenant les résultats de l'analyse de qualité
        """
        issues = []
        
        # Vérifie la présence de commentaires
        if not any(line.strip().startswith('--') for line in sql_code.split('\n')):
            issues.append({
                "type": "quality",
                "severity": "low",
                "message": "Absence de commentaires dans le code"
            })
            
        # Vérifie la convention de nommage
        if any(keyword.isupper() for keyword in ["SELECT", "FROM", "WHERE", "JOIN"]):
            issues.append({
                "type": "quality",
                "severity": "low",
                "message": "Mots-clés SQL devraient être en majuscules"
            })
            
        return {
            "quality_issues": issues,
            "quality_score": 100 - (len(issues) * 10)
        }
