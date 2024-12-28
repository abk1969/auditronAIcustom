"""Gestionnaire de configuration."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import EmailStr, HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration de l'application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='allow',
        env_nested_delimiter='__'
    )
    
    # Général
    PROJECT_NAME: str = "AuditronAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Sécurité
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    ALLOWED_HOSTS: str = "*"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    @field_validator("ALLOWED_HOSTS")
    @classmethod
    def validate_allowed_hosts(cls, v: str) -> List[str]:
        """Validate and transform allowed hosts."""
        if not v or v.strip() == "*":
            return ["*"]
        return [host.strip() for host in v.split(",") if host.strip()]

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> List[str]:
        """Validate and transform CORS origins."""
        if not v or v.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    # Base de données
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        """Assemble l'URL de connexion à la base de données."""
        if isinstance(v, str):
            return v
        
        data = info.data
        return f"postgresql+psycopg2://{data.get('POSTGRES_USER')}:{data.get('POSTGRES_PASSWORD')}@{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT', 5432)}/{data.get('POSTGRES_DB', '')}"
    
    # Redis
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Cache
    CACHE_REDIS_HOST: str = "localhost"
    CACHE_REDIS_PORT: int = 6379
    CACHE_REDIS_DB: int = 1
    CACHE_REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @field_validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        """Récupère le nom du projet si non défini."""
        if not v:
            return info.data.get("PROJECT_NAME", "AuditronAI")
        return v
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs").resolve()
    
    # Monitoring
    PROMETHEUS_MULTIPROC_DIR: Optional[Path] = (
        Path("prometheus").resolve() if os.getenv("PROMETHEUS_MULTIPROC_DIR") else None
    )
    JAEGER_AGENT_HOST: str = "localhost"
    JAEGER_AGENT_PORT: int = 6831
    
    # Stockage
    UPLOAD_DIR: Path = Path("uploads").resolve()
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif",
        ".pdf", ".doc", ".docx",
        ".xls", ".xlsx",
        ".zip", ".tar", ".gz"
    ]
    
    # Tests
    TESTING: bool = False
    TEST_DB: str = "test_db"

def get_settings() -> Settings:
    """Récupère la configuration."""
    return Settings()

# Instance globale
settings = get_settings()

# Crée les dossiers nécessaires avec des chemins absolus
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if settings.PROMETHEUS_MULTIPROC_DIR:
    settings.PROMETHEUS_MULTIPROC_DIR.mkdir(parents=True, exist_ok=True)
