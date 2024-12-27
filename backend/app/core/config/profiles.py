"""Profils de configuration pour différents environnements."""
from typing import Dict, Any
from pydantic import BaseSettings, PostgresDsn, RedisDsn
import os

class BaseProfile(BaseSettings):
    """Configuration de base commune à tous les profils."""
    APP_NAME: str = "AuditronAI"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    CORS_ORIGINS: list = ["*"]
    
    # Sécurité
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Base de données
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: str = "6379"
    
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URI(self) -> RedisDsn:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

class DevelopmentProfile(BaseProfile):
    """Configuration pour le développement local."""
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Configuration du débogage
    DEBUGGER_ENABLED: bool = True
    DEBUGGER_PORT: int = 5678
    
    # Configuration des tests
    TESTING: bool = False
    TEST_DATABASE_URI: str = "postgresql://postgres:postgres@localhost:5432/test_db"

class TestingProfile(BaseProfile):
    """Configuration pour les tests."""
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # Base de données de test
    POSTGRES_DB: str = "test_db"
    
    # Désactiver certaines fonctionnalités en test
    RATE_LIMIT_ENABLED: bool = False
    CACHE_ENABLED: bool = False

class ProductionProfile(BaseProfile):
    """Configuration pour la production."""
    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Sécurité renforcée
    CORS_ORIGINS: list = ["https://auditronai.com"]
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    PROMETHEUS_ENABLED: bool = True

# Mapping des profils
PROFILES: Dict[str, Any] = {
    "development": DevelopmentProfile,
    "testing": TestingProfile,
    "production": ProductionProfile
}

def get_profile(environment: str = None) -> BaseProfile:
    """Retourne le profil de configuration approprié."""
    env = environment or os.getenv("ENVIRONMENT", "development")
    profile_class = PROFILES.get(env.lower(), DevelopmentProfile)
    return profile_class() 