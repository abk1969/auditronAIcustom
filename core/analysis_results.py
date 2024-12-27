"""Gestion des résultats d'analyse de sécurité."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

@dataclass
class CodeQuality:
    """Métriques de qualité du code."""
    complexity: float = 0.0
    maintainability_index: float = 0.0
    functions: List[Dict[str, Any]] = field(default_factory=list)
    complex_functions: List[Dict[str, Any]] = field(default_factory=list)
    unused_code: Dict[str, Any] = field(default_factory=dict)
    style_issues: List[Dict[str, Any]] = field(default_factory=list)
    quality_summary: Dict[str, Any] = field(default_factory=dict)
    script_type: Optional[str] = None

@dataclass
class SecurityIssue:
    """Représentation d'un problème de sécurité."""
    severity: str
    confidence: str
    type: str
    description: str
    line_number: int
    code: str
    cwe: List[str]
    file: str
    more_info: str = ""
    fix_suggestions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    impact_description: str = ""
    mitigation_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'issue en dictionnaire."""
        return {
            'severity': self.severity,
            'confidence': self.confidence,
            'type': self.type,
            'description': self.description,
            'line_number': self.line_number,
            'code': self.code,
            'cwe': self.cwe,
            'file': self.file,
            'more_info': self.more_info,
            'fix_suggestions': self.fix_suggestions,
            'references': self.references,
            'impact_description': self.impact_description,
            'mitigation_steps': self.mitigation_steps
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityIssue':
        """Crée une instance à partir d'un dictionnaire."""
        return cls(
            severity=data['severity'],
            confidence=data['confidence'],
            type=data['type'],
            description=data['description'],
            line_number=data['line_number'],
            code=data['code'],
            cwe=data['cwe'],
            file=data['file'],
            more_info=data.get('more_info', ''),
            fix_suggestions=data.get('fix_suggestions', []),
            references=data.get('references', []),
            impact_description=data.get('impact_description', ''),
            mitigation_steps=data.get('mitigation_steps', [])
        )

@dataclass
class AnalysisResults:
    """Résultats d'une analyse de sécurité."""
    
    file: str
    timestamp: datetime = field(default_factory=datetime.now)
    security_issues: List[Dict[str, Any]] = field(default_factory=list)
    code_quality: CodeQuality = field(default_factory=CodeQuality)
    summary: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    code: Optional[str] = None
    filename: str = field(init=False)
    
    def __post_init__(self):
        """Initialisation post-init."""
        self.filename = Path(self.file).name
        if not self.summary:
            self.summary = {
                'severity_counts': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            }
    
    def set_code(self, code: str) -> None:
        """
        Définit le code source analysé.
        
        Args:
            code: Code source
        """
        self.code = code
        
    def add_security_issue(self, issue: SecurityIssue) -> None:
        """
        Ajoute un problème de sécurité aux résultats.
        
        Args:
            issue: Problème de sécurité à ajouter
        """
        issue_dict = issue.to_dict()
        self.security_issues.append(issue_dict)
        
        # Mettre à jour les compteurs
        severity = issue_dict['severity'].lower()
        if severity in self.summary['severity_counts']:
            self.summary['severity_counts'][severity] += 1

    def get_issues_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Récupère les problèmes par niveau de sévérité.
        
        Args:
            severity: Niveau de sévérité recherché
            
        Returns:
            Liste des problèmes correspondants
        """
        return [
            issue for issue in self.security_issues
            if issue['severity'].lower() == severity.lower()
        ]

    def get_issues_by_type(self, issue_type: str) -> List[Dict[str, Any]]:
        """
        Récupère les problèmes par type.
        
        Args:
            issue_type: Type de problème recherché
            
        Returns:
            Liste des problèmes correspondants
        """
        return [
            issue for issue in self.security_issues
            if issue['type'].lower() == issue_type.lower()
        ]

    def get_complex_functions(self, threshold: float = 10.0) -> List[Dict[str, Any]]:
        """
        Récupère les fonctions dépassant un seuil de complexité.
        
        Args:
            threshold: Seuil de complexité
            
        Returns:
            Liste des fonctions complexes
        """
        return [
            func for func in self.code_quality.functions
            if func.get('complexity', 0) > threshold
        ]

    def _update_summary(self) -> None:
        """Met à jour le résumé des résultats."""
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in self.security_issues:
            severity = issue['severity'].lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        self.summary.update({
            'total_issues': len(self.security_issues),
            'severity_counts': severity_counts,
            'complexity_score': self.code_quality.complexity,
            'maintainability_index': self.code_quality.maintainability_index,
            'complex_functions_count': len(self.code_quality.complex_functions),
            'style_issues_count': len(self.code_quality.style_issues)
        })

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit les résultats en dictionnaire.
        
        Returns:
            Dict contenant tous les résultats
        """
        return {
            'file': self.file,
            'timestamp': self.timestamp.isoformat(),
            'security_issues': self.security_issues,
            'code_quality': {
                'complexity': self.code_quality.complexity,
                'maintainability_index': self.code_quality.maintainability_index,
                'functions': self.code_quality.functions,
                'complex_functions': self.code_quality.complex_functions,
                'unused_code': self.code_quality.unused_code,
                'style_issues': self.code_quality.style_issues,
                'quality_summary': self.code_quality.quality_summary,
                'script_type': self.code_quality.script_type
            },
            'summary': self.summary,
            'metadata': self.metadata,
            'code': self.code
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResults':
        """
        Crée une instance à partir d'un dictionnaire.
        
        Args:
            data: Données des résultats
            
        Returns:
            Instance de AnalysisResults
        """
        results = cls(file=data['file'])
        results.timestamp = datetime.fromisoformat(data['timestamp'])
        results.security_issues = data['security_issues']
        
        code_quality = data['code_quality']
        results.code_quality = CodeQuality(
            complexity=code_quality['complexity'],
            maintainability_index=code_quality['maintainability_index'],
            functions=code_quality['functions'],
            complex_functions=code_quality['complex_functions'],
            unused_code=code_quality['unused_code'],
            style_issues=code_quality['style_issues'],
            quality_summary=code_quality['quality_summary'],
            script_type=code_quality.get('script_type')
        )
        
        results.summary = data['summary']
        results.metadata = data.get('metadata', {})
        results.code = data.get('code')
        
        return results

    @classmethod
    def create_default(cls) -> 'AnalysisResults':
        """
        Crée une instance par défaut.
        
        Returns:
            Instance de AnalysisResults avec des valeurs par défaut
        """
        return cls(
            file="unknown",
            security_issues=[],
            code_quality=CodeQuality(),
            summary={'error': True, 'message': "Analyse non effectuée"},
            metadata={'status': 'error'}
        )
