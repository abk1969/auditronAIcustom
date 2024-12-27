"""Système de gestion des erreurs pour AuditronAI."""
from typing import Optional, Dict, Any, List
from enum import Enum
import traceback
from dataclasses import dataclass, field
from datetime import datetime

from .logger import logger

class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ErrorCategory(Enum):
    """Catégories d'erreurs."""
    CONFIGURATION = "configuration"
    ANALYSIS = "analysis"
    SECURITY = "security"
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    PLUGIN = "plugin"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Contexte d'une erreur."""
    timestamp: datetime = field(default_factory=datetime.now)
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

class AnalysisError(Exception):
    """Exception de base pour les erreurs d'analyse."""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialise l'erreur.
        
        Args:
            message: Message d'erreur
            severity: Niveau de sévérité
            category: Catégorie d'erreur
            context: Contexte de l'erreur
            original_error: Exception d'origine si disponible
        """
        super().__init__(message)
        self.severity = severity
        self.category = category
        self.context = context or self._create_context()
        self.original_error = original_error
        
        # Journaliser l'erreur
        self._log_error()

    def _create_context(self) -> ErrorContext:
        """Crée un contexte d'erreur à partir de la stack trace."""
        tb = traceback.extract_tb(traceback.extract_stack())
        if tb:
            frame = tb[-1]  # Dernier frame de la stack
            return ErrorContext(
                file=frame.filename,
                line=frame.lineno,
                function=frame.name,
                stack_trace=traceback.format_exc()
            )
        return ErrorContext()

    def _log_error(self) -> None:
        """Journalise l'erreur avec son contexte."""
        log_message = self._format_error_message()
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _format_error_message(self) -> str:
        """Formate le message d'erreur avec le contexte."""
        parts = [
            f"[{self.severity.value.upper()}] [{self.category.value}] {str(self)}",
            f"File: {self.context.file}",
            f"Line: {self.context.line}",
            f"Function: {self.context.function}"
        ]
        
        if self.original_error:
            parts.append(f"Original error: {str(self.original_error)}")
            
        if self.context.stack_trace:
            parts.append("\nStack trace:")
            parts.append(self.context.stack_trace)
            
        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'erreur en dictionnaire.
        
        Returns:
            Dict contenant les détails de l'erreur
        """
        return {
            'message': str(self),
            'severity': self.severity.value,
            'category': self.category.value,
            'context': {
                'timestamp': self.context.timestamp.isoformat(),
                'file': self.context.file,
                'line': self.context.line,
                'function': self.context.function,
                'stack_trace': self.context.stack_trace,
                'additional_info': self.context.additional_info
            },
            'original_error': str(self.original_error) if self.original_error else None
        }

class ConfigurationError(AnalysisError):
    """Erreur de configuration."""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.CONFIGURATION,
            context=context,
            original_error=original_error
        )

class AnalyzerError(AnalysisError):
    """Erreur d'analyseur."""
    
    def __init__(
        self,
        message: str,
        analyzer_name: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        context = context or ErrorContext()
        context.additional_info['analyzer_name'] = analyzer_name
        
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.ANALYSIS,
            context=context,
            original_error=original_error
        )

class SecurityError(AnalysisError):
    """Erreur de sécurité."""
    
    def __init__(
        self,
        message: str,
        vulnerability_type: str,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None,
        cwe_ids: List[str] = None
    ):
        context = context or ErrorContext()
        context.additional_info.update({
            'vulnerability_type': vulnerability_type,
            'cwe_ids': cwe_ids or []
        })
        
        super().__init__(
            message,
            severity=severity,
            category=ErrorCategory.SECURITY,
            context=context,
            original_error=original_error
        )

def handle_analyzer_error(
    func: callable,
    analyzer_name: str,
    error_handler: Optional[callable] = None
) -> callable:
    """
    Décorateur pour gérer les erreurs des analyseurs.
    
    Args:
        func: Fonction à décorer
        analyzer_name: Nom de l'analyseur
        error_handler: Fonction de gestion d'erreur optionnelle
        
    Returns:
        Fonction décorée
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AnalysisError as e:
            # Réutiliser l'erreur existante
            if error_handler:
                return error_handler(e)
            raise
        except Exception as e:
            # Créer une nouvelle erreur d'analyseur
            error = AnalyzerError(
                message=f"Erreur lors de l'analyse avec {analyzer_name}: {str(e)}",
                analyzer_name=analyzer_name,
                original_error=e
            )
            if error_handler:
                return error_handler(error)
            raise error
    return wrapper
