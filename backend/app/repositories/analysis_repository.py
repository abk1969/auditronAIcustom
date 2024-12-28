"""Repository pour les analyses."""
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseRepository
from app.models.analysis import Analysis, AnalysisStatus
from app.core.database import get_db

class AnalysisRepository(BaseRepository[Analysis]):
    """Repository pour les analyses."""
    
    def __init__(self):
        """Initialise le repository."""
        super().__init__(Analysis)
    
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Analysis]:
        """Récupère les analyses d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            skip: Nombre d'analyses à sauter
            limit: Nombre maximum d'analyses à retourner
            
        Returns:
            Liste des analyses
        """
        query = (
            select(Analysis)
            .where(Analysis.user_id == user_id)
            .order_by(desc(Analysis.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def get_by_status(self, status: AnalysisStatus) -> List[Analysis]:
        """Récupère les analyses par statut.
        
        Args:
            status: Statut des analyses
            
        Returns:
            Liste des analyses
        """
        query = select(Analysis).where(Analysis.status == status)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def get_with_metrics(self, analysis_id: str) -> Optional[Analysis]:
        """Récupère une analyse avec ses métriques.
        
        Args:
            analysis_id: ID de l'analyse
            
        Returns:
            Analyse avec ses métriques
        """
        query = (
            select(Analysis)
            .where(Analysis.id == analysis_id)
            .options(joinedload(Analysis.metrics))
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, analysis_id: str, status: AnalysisStatus, summary: Optional[str] = None) -> Optional[Analysis]:
        """Met à jour le statut d'une analyse.
        
        Args:
            analysis_id: ID de l'analyse
            status: Nouveau statut
            summary: Résumé optionnel
            
        Returns:
            Analyse mise à jour
        """
        analysis = await self.get(analysis_id)
        if analysis:
            analysis.status = status
            if summary:
                analysis.summary = summary
            self._db.add(analysis)
            await self._db.commit()
            await self._db.refresh(analysis)
        return analysis

analysis_repository = AnalysisRepository()
