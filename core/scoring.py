"""Système de scoring pour l'analyse de sécurité."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math

@dataclass
class SecurityScore:
    """Score de sécurité."""
    total_score: float
    security_score: float
    quality_score: float
    maintainability_score: float
    details: Dict[str, Any]
    recommendations: List[str]

class SecurityScorer:
    """Calculateur de score de sécurité."""

    def __init__(self, thresholds: Dict[str, Any]):
        """
        Initialise le calculateur de score.
        
        Args:
            thresholds: Seuils de configuration
        """
        self.thresholds = thresholds
        self.severity_weights = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5
        }

    def calculate_score(
        self,
        severity_counts: Dict[str, int],
        complexity_score: float,
        max_complexity: float,
        test_coverage: Optional[float] = None,
        code_smells: Optional[int] = None
    ) -> SecurityScore:
        """
        Calcule le score global.
        
        Args:
            severity_counts: Nombre de problèmes par sévérité
            complexity_score: Score de complexité
            max_complexity: Complexité maximale autorisée
            test_coverage: Couverture de tests optionnelle
            code_smells: Nombre de code smells optionnel
            
        Returns:
            Score de sécurité calculé
        """
        # Calculer le score de sécurité (40% du total)
        security_score = self._calculate_security_score(severity_counts)
        
        # Calculer le score de qualité (30% du total)
        quality_score = self._calculate_quality_score(
            complexity_score,
            max_complexity,
            code_smells
        )
        
        # Calculer le score de maintenabilité (30% du total)
        maintainability_score = self._calculate_maintainability_score(
            complexity_score,
            test_coverage
        )
        
        # Calculer le score total pondéré
        total_score = (
            0.4 * security_score +
            0.3 * quality_score +
            0.3 * maintainability_score
        )
        
        # Générer les recommandations
        recommendations = self._generate_recommendations(
            severity_counts,
            complexity_score,
            max_complexity,
            test_coverage,
            code_smells
        )
        
        return SecurityScore(
            total_score=total_score,
            security_score=security_score,
            quality_score=quality_score,
            maintainability_score=maintainability_score,
            details={
                'severity_counts': severity_counts,
                'complexity_score': complexity_score,
                'test_coverage': test_coverage,
                'code_smells': code_smells,
                'scores': {
                    'security': security_score,
                    'quality': quality_score,
                    'maintainability': maintainability_score
                }
            },
            recommendations=recommendations
        )

    def _calculate_security_score(
        self,
        severity_counts: Dict[str, int]
    ) -> float:
        """
        Calcule le score de sécurité.
        
        Args:
            severity_counts: Nombre de problèmes par sévérité
            
        Returns:
            Score de sécurité (0-100)
        """
        max_score = 100.0
        total_weight = sum(self.severity_weights.values())
        
        # Calculer la pénalité pour chaque niveau de sévérité
        penalty = 0.0
        for severity, count in severity_counts.items():
            if count > 0 and severity in self.severity_weights:
                # Pénalité exponentielle basée sur le nombre de problèmes
                severity_penalty = (
                    self.severity_weights[severity] *
                    (1 - math.exp(-0.1 * count))
                )
                penalty += severity_penalty
        
        # Normaliser la pénalité
        normalized_penalty = (penalty / total_weight) * 100
        
        # Calculer le score final
        return max(0.0, max_score - normalized_penalty)

    def _calculate_quality_score(
        self,
        complexity_score: float,
        max_complexity: float,
        code_smells: Optional[int]
    ) -> float:
        """
        Calcule le score de qualité.
        
        Args:
            complexity_score: Score de complexité
            max_complexity: Complexité maximale autorisée
            code_smells: Nombre de code smells
            
        Returns:
            Score de qualité (0-100)
        """
        max_score = 100.0
        
        # Pénalité pour la complexité (60% du score de qualité)
        complexity_ratio = min(1.0, complexity_score / max_complexity)
        complexity_penalty = 60 * complexity_ratio
        
        # Pénalité pour les code smells (40% du score de qualité)
        smell_penalty = 0.0
        if code_smells is not None:
            # Pénalité logarithmique pour les code smells
            smell_penalty = 40 * (1 - math.exp(-0.05 * code_smells))
        
        return max(0.0, max_score - complexity_penalty - smell_penalty)

    def _calculate_maintainability_score(
        self,
        complexity_score: float,
        test_coverage: Optional[float]
    ) -> float:
        """
        Calcule le score de maintenabilité.
        
        Args:
            complexity_score: Score de complexité
            test_coverage: Couverture de tests
            
        Returns:
            Score de maintenabilité (0-100)
        """
        max_score = 100.0
        
        # Score basé sur la complexité (50% du score de maintenabilité)
        complexity_score = 50 * math.exp(-0.1 * complexity_score)
        
        # Score basé sur la couverture de tests (50% du score de maintenabilité)
        coverage_score = 0.0
        if test_coverage is not None:
            coverage_score = 50 * (test_coverage / 100)
        
        return min(max_score, complexity_score + coverage_score)

    def _generate_recommendations(
        self,
        severity_counts: Dict[str, int],
        complexity_score: float,
        max_complexity: float,
        test_coverage: Optional[float],
        code_smells: Optional[int]
    ) -> List[str]:
        """
        Génère des recommandations basées sur les métriques.
        
        Args:
            severity_counts: Nombre de problèmes par sévérité
            complexity_score: Score de complexité
            max_complexity: Complexité maximale autorisée
            test_coverage: Couverture de tests
            code_smells: Nombre de code smells
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Recommandations de sécurité
        if severity_counts.get('critical', 0) > 0:
            recommendations.append(
                "⚠️ Corriger immédiatement les vulnérabilités critiques"
            )
        if severity_counts.get('high', 0) > 0:
            recommendations.append(
                "🔴 Résoudre les vulnérabilités de haute sévérité"
            )
        if severity_counts.get('medium', 0) > 2:
            recommendations.append(
                "🟡 Réduire le nombre de vulnérabilités de moyenne sévérité"
            )
            
        # Recommandations de complexité
        if complexity_score > max_complexity:
            recommendations.append(
                "📊 Réduire la complexité cyclomatique du code"
            )
            
        # Recommandations de tests
        if test_coverage is not None and test_coverage < 80:
            recommendations.append(
                "🧪 Augmenter la couverture des tests (objectif: 80%)"
            )
            
        # Recommandations de qualité
        if code_smells is not None and code_smells > 10:
            recommendations.append(
                "🔍 Réduire le nombre de code smells"
            )
            
        return recommendations

    def get_grade(self, score: float) -> str:
        """
        Convertit un score en grade.
        
        Args:
            score: Score à convertir
            
        Returns:
            Grade (A+ à F)
        """
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        elif score >= 55:
            return 'C-'
        elif score >= 50:
            return 'D+'
        elif score >= 45:
            return 'D'
        elif score >= 40:
            return 'D-'
        else:
            return 'F'
