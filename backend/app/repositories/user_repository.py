"""Repository spécifique pour les utilisateurs."""
from typing import Optional, List
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        stmt = select(self.model).where(self.model.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all() 