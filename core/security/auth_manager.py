"""Gestionnaire d'authentification pour AuditronAI."""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException
from pydantic import BaseModel

from .security_config import security_settings
from .security_auditor import security_auditor
from .secrets_manager import secrets_manager

class TokenPayload(BaseModel):
    """Modèle pour le payload du token JWT."""
    
    sub: str  # Subject (user_id)
    exp: datetime  # Expiration
    iat: datetime  # Issued at
    type: str  # Type de token (access/refresh)
    roles: list[str]  # Rôles de l'utilisateur

class AuthManager:
    """Gestionnaire d'authentification."""

    def __init__(self) -> None:
        """Initialise le gestionnaire d'authentification."""
        self._jwt_secret = secrets_manager.get_secret("JWT_SECRET")
        if not self._jwt_secret:
            raise ValueError("JWT_SECRET non défini")

    def hash_password(self, password: str) -> str:
        """Hash un mot de passe avec bcrypt.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Hash du mot de passe
        """
        salt = bcrypt.gensalt(rounds=security_settings.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Vérifie un mot de passe.
        
        Args:
            password: Mot de passe en clair
            hashed: Hash du mot de passe
            
        Returns:
            True si le mot de passe est valide
        """
        try:
            return bcrypt.checkpw(
                password.encode(),
                hashed.encode()
            )
        except Exception:
            return False

    def create_access_token(
        self,
        user_id: str,
        roles: list[str]
    ) -> str:
        """Crée un token d'accès JWT.
        
        Args:
            user_id: ID de l'utilisateur
            roles: Rôles de l'utilisateur
            
        Returns:
            Token JWT
        """
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=user_id,
            exp=now + timedelta(
                minutes=security_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            iat=now,
            type="access",
            roles=roles
        )
        
        return jwt.encode(
            payload.dict(),
            self._jwt_secret,
            algorithm=security_settings.JWT_ALGORITHM
        )

    def create_refresh_token(
        self,
        user_id: str,
        roles: list[str]
    ) -> str:
        """Crée un token de rafraîchissement JWT.
        
        Args:
            user_id: ID de l'utilisateur
            roles: Rôles de l'utilisateur
            
        Returns:
            Token JWT
        """
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=user_id,
            exp=now + timedelta(
                days=security_settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            ),
            iat=now,
            type="refresh",
            roles=roles
        )
        
        return jwt.encode(
            payload.dict(),
            self._jwt_secret,
            algorithm=security_settings.JWT_ALGORITHM
        )

    def verify_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Optional[TokenPayload]:
        """Vérifie un token JWT.
        
        Args:
            token: Token JWT
            token_type: Type de token attendu
            
        Returns:
            Payload du token si valide
            
        Raises:
            HTTPException: Si le token est invalide
        """
        try:
            payload = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=[security_settings.JWT_ALGORITHM]
            )
            
            token_data = TokenPayload(**payload)
            
            if token_data.type != token_type:
                raise HTTPException(
                    status_code=401,
                    detail="Type de token invalide"
                )
                
            return token_data
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Token invalide"
            )

    def authenticate_request(
        self,
        request: Request
    ) -> Tuple[str, list[str]]:
        """Authentifie une requête.
        
        Args:
            request: Requête à authentifier
            
        Returns:
            Tuple (user_id, roles)
            
        Raises:
            HTTPException: Si l'authentification échoue
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Token manquant"
            )
            
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Schéma d'authentification invalide"
                )
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Format de token invalide"
            )
            
        payload = self.verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=401,
                detail="Token invalide"
            )
            
        return payload.sub, payload.roles

    def check_permission(
        self,
        required_roles: list[str],
        user_roles: list[str]
    ) -> bool:
        """Vérifie les permissions d'un utilisateur.
        
        Args:
            required_roles: Rôles requis
            user_roles: Rôles de l'utilisateur
            
        Returns:
            True si l'utilisateur a les permissions
        """
        return any(role in user_roles for role in required_roles)

    def rotate_jwt_secret(self) -> None:
        """Effectue une rotation de la clé secrète JWT."""
        new_secret = secrets_manager.get_secret("NEW_JWT_SECRET")
        if not new_secret:
            raise ValueError("NEW_JWT_SECRET non défini")
            
        old_secret = self._jwt_secret
        self._jwt_secret = new_secret
        
        secrets_manager.set_secret("JWT_SECRET", new_secret)
        secrets_manager.delete_secret("NEW_JWT_SECRET")
        
        security_auditor.log_security_event(
            event_type="jwt_secret_rotated",
            description="Rotation de la clé secrète JWT effectuée",
            severity="INFO"
        )

# Instance globale du gestionnaire d'authentification
auth_manager = AuthManager() 