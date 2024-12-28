"""Configuration de sécurité centralisée pour AuditronAI."""

from typing import Dict, List, Optional
from pydantic import SecretStr, validator
from pydantic_settings import BaseSettings
import ssl

class SecuritySettings(BaseSettings):
    """Paramètres de sécurité globaux."""
    
    # Paramètres JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_MIN_LENGTH: int = 32

    # Paramètres de hachage
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    BCRYPT_ROUNDS: int = 12
    
    # Paramètres SSL/TLS
    SSL_VERSION: int = ssl.PROTOCOL_TLS_SERVER
    SSL_VERIFY_MODE: int = ssl.CERT_REQUIRED
    SSL_CHECK_HOSTNAME: bool = True
    MINIMUM_TLS_VERSION: float = 1.2

    # En-têtes de sécurité
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self';",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    # Paramètres de rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # secondes

    # Paramètres de session
    SESSION_SECURE: bool = True
    SESSION_HTTPONLY: bool = True
    SESSION_SAMESITE: str = "Strict"
    SESSION_MAX_AGE: int = 3600  # secondes

    # Paramètres de validation des entrées
    INPUT_MAX_LENGTH: int = 1000
    ALLOWED_CONTENT_TYPES: List[str] = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ]
    FILE_UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [".py", ".ts", ".js", ".sql"]

    # Paramètres de journalisation de sécurité
    SECURITY_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_ENABLED: bool = True
    SENSITIVE_FIELDS: List[str] = [
        "password",
        "token",
        "api_key",
        "secret",
        "credit_card"
    ]

    # Paramètres de base de données
    DB_CONNECTION_TIMEOUT: int = 5
    DB_POOL_RECYCLE: int = 3600
    DB_SSL_REQUIRED: bool = True
    DB_STATEMENT_TIMEOUT: int = 30  # secondes

    # Paramètres de cache
    CACHE_SSL_REQUIRED: bool = True
    CACHE_MAX_MEMORY: int = 128 * 1024 * 1024  # 128MB
    CACHE_TTL: int = 3600  # secondes

    @validator("MINIMUM_TLS_VERSION")
    def validate_tls_version(cls, v: float) -> float:
        """Valide la version minimale de TLS."""
        if v < 1.2:
            raise ValueError("La version minimale de TLS doit être >= 1.2")
        return v

    @validator("BCRYPT_ROUNDS")
    def validate_bcrypt_rounds(cls, v: int) -> int:
        """Valide le nombre de rounds bcrypt."""
        if v < 12:
            raise ValueError("Le nombre de rounds bcrypt doit être >= 12")
        return v

    class Config:
        """Configuration Pydantic."""
        case_sensitive = True
        env_prefix = "SECURITY_"

security_settings = SecuritySettings() 