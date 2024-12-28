"""Middleware de limitation de taux."""

from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import RateLimitException
from app.core.logging import get_logger

logger = get_logger(__name__)

class RateLimiter:
    """Gestionnaire de limitation de taux."""
    
    def __init__(self, window_size: int = 60, max_requests: int = 60):
        """Initialise le gestionnaire.
        
        Args:
            window_size: Taille de la fenêtre en secondes
            max_requests: Nombre maximum de requêtes
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: Dict[str, list[datetime]] = {}
        self.blocked: Dict[str, datetime] = {}
    
    def is_blocked(self, key: str) -> bool:
        """Vérifie si une clé est bloquée.
        
        Args:
            key: Clé à vérifier
            
        Returns:
            True si bloquée
        """
        if key in self.blocked:
            if datetime.utcnow() >= self.blocked[key]:
                del self.blocked[key]
                return False
            return True
        return False
    
    def block(self, key: str, duration: int = 300):
        """Bloque une clé.
        
        Args:
            key: Clé à bloquer
            duration: Durée du blocage en secondes
        """
        self.blocked[key] = datetime.utcnow() + timedelta(seconds=duration)
    
    def add_request(self, key: str) -> Tuple[bool, Optional[int]]:
        """Ajoute une requête.
        
        Args:
            key: Clé de la requête
            
        Returns:
            Tuple (autorisé, temps restant)
        """
        now = datetime.utcnow()
        
        # Vérifie si la clé est bloquée
        if self.is_blocked(key):
            remaining = int(
                (self.blocked[key] - now).total_seconds()
            )
            return False, remaining
        
        # Initialise la liste des requêtes
        if key not in self.requests:
            self.requests[key] = []
        
        # Supprime les requêtes expirées
        window_start = now - timedelta(seconds=self.window_size)
        self.requests[key] = [
            req for req in self.requests[key]
            if req >= window_start
        ]
        
        # Vérifie la limite
        if len(self.requests[key]) >= self.max_requests:
            # Bloque la clé si trop de requêtes
            self.block(key)
            return False, 300
        
        # Ajoute la requête
        self.requests[key].append(now)
        return True, None
    
    def get_remaining(self, key: str) -> Tuple[int, int]:
        """Récupère le nombre de requêtes restantes.
        
        Args:
            key: Clé à vérifier
            
        Returns:
            Tuple (requêtes restantes, temps restant)
        """
        now = datetime.utcnow()
        
        # Vérifie si la clé est bloquée
        if self.is_blocked(key):
            remaining = int(
                (self.blocked[key] - now).total_seconds()
            )
            return 0, remaining
        
        # Vérifie les requêtes
        if key not in self.requests:
            return self.max_requests, self.window_size
        
        # Supprime les requêtes expirées
        window_start = now - timedelta(seconds=self.window_size)
        self.requests[key] = [
            req for req in self.requests[key]
            if req >= window_start
        ]
        
        # Calcule le temps restant
        if self.requests[key]:
            oldest = min(self.requests[key])
            reset = int(
                (oldest + timedelta(seconds=self.window_size) - now).total_seconds()
            )
        else:
            reset = self.window_size
        
        return self.max_requests - len(self.requests[key]), reset

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitation de taux."""
    
    def __init__(
        self,
        app,
        window_size: int = 60,
        max_requests: int = 60,
        exclude_paths: Optional[list[str]] = None
    ):
        """Initialise le middleware.
        
        Args:
            app: Application FastAPI
            window_size: Taille de la fenêtre en secondes
            max_requests: Nombre maximum de requêtes
            exclude_paths: Chemins à exclure
        """
        super().__init__(app)
        self.limiter = RateLimiter(window_size, max_requests)
        self.exclude_paths = exclude_paths or []
    
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
            
            # Récupère l'IP du client
            client_ip = request.client.host
            
            # Vérifie la limite
            allowed, blocked_time = self.limiter.add_request(client_ip)
            if not allowed:
                raise RateLimitException(
                    f"Trop de requêtes. Réessayez dans {blocked_time} secondes."
                )
            
            # Exécute la requête
            response = await call_next(request)
            
            # Ajoute les en-têtes de limite
            remaining, reset = self.limiter.get_remaining(client_ip)
            response.headers["X-RateLimit-Limit"] = str(
                settings.RATE_LIMIT_PER_MINUTE
            )
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)
            
            return response
            
        except Exception as e:
            logger.error(
                "Erreur de limitation",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e)
                }
            )
            
            if isinstance(e, RateLimitException):
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": str(e)}
                )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne du serveur"}
            ) 