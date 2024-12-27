"""Exceptions personnalisées."""

from typing import Any, Dict, Optional

class BaseException(Exception):
    """Exception de base."""
    
    def __init__(
        self,
        message: str,
        code: str = "error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            code: Code d'erreur
            status_code: Code HTTP
            details: Détails supplémentaires
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

class ValidationException(BaseException):
    """Exception de validation."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails de validation
        """
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            details=details
        )

class NotFoundException(BaseException):
    """Exception ressource non trouvée."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="not_found",
            status_code=404,
            details=details
        )

class CredentialsException(BaseException):
    """Exception d'authentification."""
    
    def __init__(
        self,
        message: str = "Identifiants invalides",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="invalid_credentials",
            status_code=401,
            details=details
        )

class PermissionDeniedException(BaseException):
    """Exception de permission."""
    
    def __init__(
        self,
        message: str = "Permission refusée",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="permission_denied",
            status_code=403,
            details=details
        )

class ConflictException(BaseException):
    """Exception de conflit."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="conflict",
            status_code=409,
            details=details
        )

class RateLimitException(BaseException):
    """Exception de limite de requêtes."""
    
    def __init__(
        self,
        message: str = "Trop de requêtes",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="rate_limit",
            status_code=429,
            details=details
        )

class ServiceUnavailableException(BaseException):
    """Exception de service indisponible."""
    
    def __init__(
        self,
        message: str = "Service temporairement indisponible",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialise l'exception.
        
        Args:
            message: Message d'erreur
            details: Détails supplémentaires
        """
        super().__init__(
            message=message,
            code="service_unavailable",
            status_code=503,
            details=details
        ) 