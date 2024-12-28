"""Gestionnaire d'authentification."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import monitoring
from app.db.session import get_db
from app.models.user import User

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class AuthManager:
    """Gestionnaire d'authentification."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.pwd_context = pwd_context
        self.oauth2_scheme = oauth2_scheme
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe.
        
        Args:
            plain_password: Mot de passe en clair
            hashed_password: Hash du mot de passe
            
        Returns:
            True si le mot de passe est valide
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash un mot de passe.
        
        Args:
            password: Mot de passe à hasher
            
        Returns:
            Hash du mot de passe
        """
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self,
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crée un token d'accès.
        
        Args:
            subject: Sujet du token
            expires_delta: Durée de validité
            
        Returns:
            Token d'accès
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, subject: Union[str, Any]) -> str:
        """Crée un token de rafraîchissement.
        
        Args:
            subject: Sujet du token
            
        Returns:
            Token de rafraîchissement
        """
        expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Décode un token.
        
        Args:
            token: Token à décoder
            
        Returns:
            Contenu du token
            
        Raises:
            HTTPException: Si le token est invalide
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
    
    def get_current_user(
        self,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> User:
        """Récupère l'utilisateur courant.
        
        Args:
            db: Session de base de données
            token: Token d'accès
            
        Returns:
            Utilisateur courant
            
        Raises:
            HTTPException: Si l'utilisateur n'existe pas
        """
        try:
            payload = self.decode_token(token)
            user_id: str = payload["sub"]
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return user
    
    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authentifie un utilisateur.
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe
            
        Returns:
            Utilisateur authentifié ou None
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            monitoring.track_auth(success=False)
            return None
        
        if not self.verify_password(password, user.hashed_password):
            monitoring.track_auth(success=False)
            return None
        
        monitoring.track_auth(success=True)
        return user
    
    def check_permissions(self, user: User, required_permissions: list[str]) -> bool:
        """Vérifie les permissions d'un utilisateur.
        
        Args:
            user: Utilisateur à vérifier
            required_permissions: Permissions requises
            
        Returns:
            True si l'utilisateur a les permissions
        """
        if user.is_superuser:
            return True
            
        user_permissions = set(user.permissions)
        required = set(required_permissions)
        
        return required.issubset(user_permissions)

# Instance globale
auth_manager = AuthManager() 