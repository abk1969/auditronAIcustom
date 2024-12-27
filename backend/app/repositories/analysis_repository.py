"""Repository spécifique pour les analyses."""
from typing import List, Optional
from sqlalchemy import select, desc
from app.models.analysis import Analysis, AnalysisStatus
from app.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[Analysis]):
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Analysis]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(self, status: AnalysisStatus) -> List[Analysis]:
        stmt = select(self.model).where(self.model.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_metrics(self, analysis_id: str) -> Optional[Analysis]:
        stmt = (
            select(self.model)
            .where(self.model.id == analysis_id)
            .options(joinedload(self.model.metrics))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() 