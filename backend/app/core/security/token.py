"""Utilitaires de gestion des tokens."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4
import jwt

from app.core.config import settings

def create_token(
    data: Dict[str, Any],
    secret_key: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crée un token JWT.
    
    Args:
        data: Données à encoder
        secret_key: Clé secrète
        expires_delta: Durée de validité
        
    Returns:
        Token JWT
    """
    to_encode = data.copy()
    
    # Ajoute l'expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid4())
    })
    
    # Encode le token
    return jwt.encode(
        to_encode,
        secret_key or settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithms: Optional[list[str]] = None
) -> Optional[Dict[str, Any]]:
    """Décode un token JWT.
    
    Args:
        token: Token JWT
        secret_key: Clé secrète
        algorithms: Algorithmes de décodage
        
    Returns:
        Données décodées ou None si invalide
    """
    try:
        return jwt.decode(
            token,
            secret_key or settings.SECRET_KEY,
            algorithms=algorithms or [settings.JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        return None

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crée un token d'accès.
    
    Args:
        subject: Sujet du token
        expires_delta: Durée de validité
        
    Returns:
        Token d'accès
    """
    return create_token(
        data={"sub": subject, "type": "access"},
        expires_delta=expires_delta
    )

def create_refresh_token(subject: str) -> str:
    """Crée un token de rafraîchissement.
    
    Args:
        subject: Sujet du token
        
    Returns:
        Token de rafraîchissement
    """
    return create_token(
        data={"sub": subject, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def create_password_reset_token(email: str) -> str:
    """Crée un token de réinitialisation de mot de passe.
    
    Args:
        email: Email de l'utilisateur
        
    Returns:
        Token de réinitialisation
    """
    return create_token(
        data={"sub": email, "type": "reset"},
        expires_delta=timedelta(hours=settings.RESET_TOKEN_EXPIRE_HOURS)
    )

def create_email_verification_token(email: str) -> str:
    """Crée un token de vérification d'email.
    
    Args:
        email: Email de l'utilisateur
        
    Returns:
        Token de vérification
    """
    return create_token(
        data={"sub": email, "type": "verify"},
        expires_delta=timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    ) 