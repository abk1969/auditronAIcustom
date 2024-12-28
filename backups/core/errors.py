"""Gestionnaire d'erreurs."""

from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.logging import get_logger

logger = get_logger(__name__)

class APIError(Exception):
    """Erreur API personnalisée."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'erreur.
        
        Args:
            message: Message d'erreur
            status_code: Code de statut HTTP
            error_code: Code d'erreur interne
            details: Détails supplémentaires
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class ErrorManager:
    """Gestionnaire d'erreurs."""
    
    def __init__(self, app: FastAPI):
        """Initialise le gestionnaire.
        
        Args:
            app: Application FastAPI
        """
        self.app = app
        self.setup_handlers()
    
    def setup_handlers(self) -> None:
        """Configure les gestionnaires d'erreurs."""
        
        @self.app.exception_handler(APIError)
        async def api_error_handler(
            request: Request,
            exc: APIError
        ) -> JSONResponse:
            """Gère les erreurs API personnalisées.
            
            Args:
                request: Requête
                exc: Exception
                
            Returns:
                Réponse JSON
            """
            error_response = {
                "error": {
                    "message": exc.message,
                    "code": exc.error_code,
                    "details": exc.details,
                    "type": "api_error"
                }
            }
            
            logger.error(
                "Erreur API",
                extra={
                    "error": error_response,
                    "status_code": exc.status_code,
                    "path": request.url.path
                }
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_error_handler(
            request: Request,
            exc: RequestValidationError
        ) -> JSONResponse:
            """Gère les erreurs de validation.
            
            Args:
                request: Requête
                exc: Exception
                
            Returns:
                Réponse JSON
            """
            error_response = {
                "error": {
                    "message": "Erreur de validation des données",
                    "code": "VALIDATION_ERROR",
                    "details": exc.errors(),
                    "type": "validation_error"
                }
            }
            
            logger.error(
                "Erreur de validation",
                extra={
                    "error": error_response,
                    "path": request.url.path
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response
            )
        
        @self.app.exception_handler(ValidationError)
        async def pydantic_error_handler(
            request: Request,
            exc: ValidationError
        ) -> JSONResponse:
            """Gère les erreurs de validation Pydantic.
            
            Args:
                request: Requête
                exc: Exception
                
            Returns:
                Réponse JSON
            """
            error_response = {
                "error": {
                    "message": "Erreur de validation des données",
                    "code": "VALIDATION_ERROR",
                    "details": exc.errors(),
                    "type": "validation_error"
                }
            }
            
            logger.error(
                "Erreur de validation Pydantic",
                extra={
                    "error": error_response,
                    "path": request.url.path
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=error_response
            )
        
        @self.app.exception_handler(SQLAlchemyError)
        async def sqlalchemy_error_handler(
            request: Request,
            exc: SQLAlchemyError
        ) -> JSONResponse:
            """Gère les erreurs de base de données.
            
            Args:
                request: Requête
                exc: Exception
                
            Returns:
                Réponse JSON
            """
            error_response = {
                "error": {
                    "message": "Erreur de base de données",
                    "code": "DATABASE_ERROR",
                    "details": {"error": str(exc)},
                    "type": "database_error"
                }
            }
            
            logger.error(
                "Erreur de base de données",
                extra={
                    "error": error_response,
                    "path": request.url.path
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )
        
        @self.app.exception_handler(Exception)
        async def general_error_handler(
            request: Request,
            exc: Exception
        ) -> JSONResponse:
            """Gère les erreurs générales.
            
            Args:
                request: Requête
                exc: Exception
                
            Returns:
                Réponse JSON
            """
            error_response = {
                "error": {
                    "message": "Erreur interne du serveur",
                    "code": "INTERNAL_ERROR",
                    "details": {"error": str(exc)},
                    "type": "internal_error"
                }
            }
            
            logger.error(
                "Erreur interne",
                extra={
                    "error": error_response,
                    "path": request.url.path
                },
                exc_info=True
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )

def setup_error_handling(app: FastAPI) -> None:
    """Configure la gestion des erreurs.
    
    Args:
        app: Application FastAPI
    """
    ErrorManager(app) 