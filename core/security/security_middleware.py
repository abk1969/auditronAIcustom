"""Middleware de sécurité pour AuditronAI."""

from functools import wraps
from typing import Any, Callable, Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .input_validator import input_validator, SecurityValidationError
from .security_config import security_settings

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware appliquant les règles de sécurité."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Traite la requête en appliquant les règles de sécurité.
        
        Args:
            request: La requête entrante
            call_next: La fonction à appeler ensuite
            
        Returns:
            La réponse
        """
        try:
            # Validation des headers
            await self._validate_headers(request)
            
            # Validation du body si présent
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.json()
                input_validator.validate_json_structure(body, [])
            
            # Validation des query params
            for param in request.query_params.values():
                input_validator.validate_string_input(param)
                
            # Validation des path params  
            for param in request.path_params.values():
                if isinstance(param, str):
                    input_validator.validate_string_input(param)
            
            response = await call_next(request)
            
            # Ajout des headers de sécurité
            response.headers.update(self._get_security_headers())
            
            return response
            
        except SecurityValidationError as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e)}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500, 
                content={"error": "Erreur interne du serveur"}
            )
            
    async def _validate_headers(self, request: Request) -> None:
        """Valide les headers de la requête.
        
        Args:
            request: La requête à valider
            
        Raises:
            SecurityValidationError: Si la validation échoue
        """
        # Vérifie le Content-Type
        content_type = request.headers.get("content-type", "")
        if request.method in ["POST", "PUT", "PATCH"]:
            if not content_type.startswith("application/json"):
                raise SecurityValidationError(
                    "Content-Type doit être application/json"
                )
                
        # Vérifie les headers de sécurité requis
        for header in security_settings.REQUIRED_HEADERS:
            if header not in request.headers:
                raise SecurityValidationError(
                    f"Header requis manquant: {header}"
                )
                
        # Valide les valeurs des headers
        for name, value in request.headers.items():
            input_validator.validate_string_input(
                value, 
                security_settings.HEADER_MAX_LENGTH
            )
            
    def _get_security_headers(self) -> Dict[str, str]:
        """Retourne les headers de sécurité à ajouter.
        
        Returns:
            Les headers de sécurité
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cache-Control": "no-store, max-age=0",
            "Clear-Site-Data": '"cache", "cookies", "storage"'
        }

def validate_input(func: Callable) -> Callable:
    """Décorateur pour valider les entrées d'une fonction.
    
    Args:
        func: La fonction à décorer
        
    Returns:
        La fonction décorée
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Valide les arguments
        for arg in args:
            if isinstance(arg, str):
                input_validator.validate_string_input(arg)
                
        # Valide les kwargs
        for value in kwargs.values():
            if isinstance(value, str):
                input_validator.validate_string_input(value)
                
        return func(*args, **kwargs)
        
    return wrapper 