"""Gestionnaire de configuration."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, EmailStr, PostgresDsn, validator

class Settings(BaseSettings):
    """Configuration de l'application."""
    
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
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    
    # Base de données
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Assemble l'URL de connexion à la base de données.
        
        Args:
            v: Valeur actuelle
            values: Valeurs de configuration
            
        Returns:
            URL de connexion
        """
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Cache
    CACHE_REDIS_HOST: str = "localhost"
    CACHE_REDIS_PORT: int = 6379
    CACHE_REDIS_DB: int = 1
    CACHE_REDIS_PASSWORD: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Récupère le nom du projet si non défini.
        
        Args:
            v: Valeur actuelle
            values: Valeurs de configuration
            
        Returns:
            Nom du projet
        """
        if not v:
            return values["PROJECT_NAME"]
        return v
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    
    # Monitoring
    PROMETHEUS_MULTIPROC_DIR: Optional[Path] = None
    JAEGER_AGENT_HOST: str = "localhost"
    JAEGER_AGENT_PORT: int = 6831
    
    # Stockage
    UPLOAD_DIR: Path = Path("uploads")
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
    
    class Config:
        """Configuration Pydantic."""
        
        case_sensitive = True
        env_file = ".env"

def get_settings() -> Settings:
    """Récupère la configuration.
    
    Returns:
        Configuration
    """
    return Settings()

# Instance globale
settings = get_settings()

# Crée les dossiers nécessaires
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

if settings.PROMETHEUS_MULTIPROC_DIR:
    settings.PROMETHEUS_MULTIPROC_DIR.mkdir(parents=True, exist_ok=True) 