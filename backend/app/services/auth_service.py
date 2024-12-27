"""Service d'authentification."""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from app.core.config import get_settings
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.security import verify_password, get_password_hash

settings = get_settings()

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_access_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "exp": expire,
            "sub": str(user_id),
            "type": "access"
        }
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get("sub")
            if not user_id:
                return None
            return await self.repository.get(user_id)
        except jwt.JWTError:
            return None 