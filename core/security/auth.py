"""Système d'authentification JWT."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

class AuthManager:
    """Gestionnaire d'authentification."""
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification."""
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
        self.algorithm = "HS256"
        self.security = HTTPBearer()
        
    @telemetry.trace_method("create_token")
    def create_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT."""
        try:
            expires = datetime.utcnow() + (expires_delta or timedelta(days=1))
            
            payload = {
                'sub': user_id,
                'exp': expires,
                'iat': datetime.utcnow()
            }
            
            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du token: {e}")
            raise
    
    @telemetry.trace_method("verify_token")
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Dict[str, Any]:
        """Vérifie un token JWT."""
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            if payload['exp'] < datetime.utcnow().timestamp():
                raise HTTPException(401, "Token expiré")
                
            return payload
            
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Token invalide")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du token: {e}")
            raise HTTPException(401, "Erreur d'authentification") 