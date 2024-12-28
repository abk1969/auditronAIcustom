"""Schémas Pydantic pour les analyses."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field

class Analysis(BaseModel):
    """Modèle d'analyse."""
    
    id: str = Field(..., description="Identifiant unique de l'analyse")
    user_id: str = Field(..., description="Identifiant de l'utilisateur")
    repository_name: str = Field(..., description="Nom du dépôt ou du fichier analysé")
    language: str = Field(..., description="Langage de programmation détecté")
    status: str = Field(..., description="Statut de l'analyse")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Métriques de l'analyse")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Problèmes détectés")
    suggestions: List[Dict[str, Any]] = Field(default_factory=list, description="Suggestions d'amélioration")
    summary: str = Field(..., description="Résumé de l'analyse")
    lines_of_code: int = Field(..., description="Nombre de lignes de code")
    complexity_score: float = Field(..., description="Score de complexité")
    security_score: float = Field(..., description="Score de sécurité")
    performance_score: float = Field(..., description="Score de performance")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    class Config:
        """Configuration du modèle."""
        
        from_attributes = True

class AnalysisResponse(BaseModel):
    """Réponse d'analyse."""
    
    success: bool = Field(..., description="Statut de la réponse")
    data: Analysis = Field(..., description="Données de l'analyse")
    message: str = Field(..., description="Message de la réponse")

class AnalysisListResponse(BaseModel):
    """Réponse de liste d'analyses."""
    
    success: bool = Field(..., description="Statut de la réponse")
    data: List[Analysis] = Field(..., description="Liste des analyses")
    message: str = Field(..., description="Message de la réponse")

class AnalysisStats(BaseModel):
    """Statistiques d'analyse."""
    
    total_scans: int = Field(..., description="Nombre total d'analyses")
    issues_found: int = Field(..., description="Nombre de problèmes trouvés")
    issues_resolved: int = Field(..., description="Nombre de problèmes résolus")
    average_resolution_time: str = Field(..., description="Temps moyen de résolution")

class AnalysisStatsResponse(BaseModel):
    """Réponse de statistiques d'analyse."""
    
    success: bool = Field(..., description="Statut de la réponse")
    data: AnalysisStats = Field(..., description="Statistiques")
    message: str = Field(..., description="Message de la réponse")

class GitRepositoryRequest(BaseModel):
    """Requête d'analyse de dépôt Git."""
    
    url: str = Field(..., description="URL du dépôt Git")
    branch: Optional[str] = Field(None, description="Branche à analyser")
    commit: Optional[str] = Field(None, description="Commit à analyser") 