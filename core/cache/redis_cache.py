"""Module de cache Redis pour AuditronAI."""
import redis
from typing import Any, Optional
import pickle
import json
from datetime import timedelta
from ..logger import logger

class RedisCache:
    """Gestionnaire de cache Redis."""
    
    def __init__(self, host: str, port: int, password: Optional[str] = None):
        """Initialise la connexion Redis."""
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                password=password,
                decode_responses=False
            )
            logger.info("Connexion Redis établie")
        except redis.ConnectionError as e:
            logger.error(f"Erreur de connexion Redis: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache."""
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl: Durée de vie en secondes
        """
        try:
            serialized = pickle.dumps(value)
            return self.redis.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans le cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Supprime une clé du cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache: {e}")
            return False 