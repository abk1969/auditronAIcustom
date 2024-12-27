"""Middleware de sécurité."""

from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.security.token import decode_token
from app.core.exceptions import CredentialsException, PermissionDeniedException
from app.core.logging import get_logger

logger = get_logger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité."""
    
    def __init__(
        self,
        app,
        exclude_paths: Optional[list[str]] = None
    ):
        """Initialise le middleware.
        
        Args:
            app: Application FastAPI
            exclude_paths: Chemins à exclure
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.security = HTTPBearer()
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Traite une requête.
        
        Args:
            request: Requête HTTP
            call_next: Fonction suivante
            
        Returns:
            Réponse HTTP
        """
        try:
            # Vérifie si le chemin est exclu
            if any(request.url.path.startswith(path) for path in self.exclude_paths):
                return await call_next(request)
            
            # Vérifie le token
            token = await self._get_token(request)
            if not token:
                raise CredentialsException()
            
            # Décode le token
            payload = decode_token(token)
            if not payload:
                raise CredentialsException()
            
            # Vérifie les permissions
            if not await self._check_permissions(request, payload):
                raise PermissionDeniedException()
            
            # Ajoute les en-têtes de sécurité
            response = await call_next(request)
            return self._add_security_headers(response)
            
        except Exception as e:
            logger.error(
                "Erreur de sécurité",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e)
                }
            )
            
            if isinstance(e, (CredentialsException, PermissionDeniedException)):
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": str(e)}
                )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne du serveur"}
            )
    
    async def _get_token(self, request: Request) -> Optional[str]:
        """Récupère le token d'authentification.
        
        Args:
            request: Requête HTTP
            
        Returns:
            Token d'authentification
        """
        try:
            credentials = await self.security(request)
            return credentials.credentials
        except:
            return None
    
    async def _check_permissions(
        self,
        request: Request,
        payload: dict
    ) -> bool:
        """Vérifie les permissions.
        
        Args:
            request: Requête HTTP
            payload: Données du token
            
        Returns:
            True si autorisé
        """
        # TODO: Implémenter la vérification des permissions
        return True
    
    def _add_security_headers(self, response: Response) -> Response:
        """Ajoute les en-têtes de sécurité.
        
        Args:
            response: Réponse HTTP
            
        Returns:
            Réponse avec en-têtes
        """
        # Protection XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Protection clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Protection MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Politique de sécurité du contenu
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        # Référent
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS
        if settings.BACKEND_CORS_ORIGINS:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        return response 