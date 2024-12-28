"""Gestionnaire de cache."""

import json
import pickle
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Optional, Union

import redis
from redis.client import Redis

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import monitoring

logger = get_logger(__name__)

class CacheManager:
    """Gestionnaire de cache."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.redis: Redis = redis.Redis(
            host=settings.CACHE_REDIS_HOST,
            port=settings.CACHE_REDIS_PORT,
            db=settings.CACHE_REDIS_DB,
            password=settings.CACHE_REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Vérifie la connexion
        try:
            self.redis.ping()
            logger.info("Connexion au cache Redis établie")
        except redis.ConnectionError as e:
            logger.error(
                "Erreur de connexion au cache Redis",
                extra={"error": str(e)}
            )
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache.
        
        Args:
            key: Clé à récupérer
            
        Returns:
            Valeur ou None
        """
        try:
            value = self.redis.get(key)
            if value:
                monitoring.track_cache("redis", hit=True)
                return json.loads(value)
            
            monitoring.track_cache("redis", hit=False)
            return None
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération du cache",
                extra={"error": str(e), "key": key}
            )
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Définit une valeur dans le cache.
        
        Args:
            key: Clé à définir
            value: Valeur à stocker
            expire: Durée d'expiration
            
        Returns:
            True si succès
        """
        try:
            # Convertit la valeur en JSON
            json_value = json.dumps(value)
            
            # Définit la valeur
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                self.redis.setex(key, expire, json_value)
            else:
                self.redis.set(key, json_value)
            
            # Met à jour les métriques
            monitoring.track_cache(
                "redis",
                hit=True,
                size=len(json_value.encode())
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Erreur lors de la définition du cache",
                extra={"error": str(e), "key": key}
            )
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une valeur du cache.
        
        Args:
            key: Clé à supprimer
            
        Returns:
            True si succès
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(
                "Erreur lors de la suppression du cache",
                extra={"error": str(e), "key": key}
            )
            return False
    
    def clear(self) -> bool:
        """Vide le cache.
        
        Returns:
            True si succès
        """
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(
                "Erreur lors du vidage du cache",
                extra={"error": str(e)}
            )
            return False
    
    def cached(
        self,
        key_prefix: str,
        expire: Optional[Union[int, timedelta]] = None
    ) -> Callable:
        """Décorateur pour mettre en cache le résultat d'une fonction.
        
        Args:
            key_prefix: Préfixe de la clé
            expire: Durée d'expiration
            
        Returns:
            Décorateur
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Génère la clé
                key_parts = [key_prefix]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
                
                # Vérifie le cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Exécute la fonction
                result = await func(*args, **kwargs)
                
                # Met en cache
                self.set(cache_key, result, expire)
                
                return result
            
            return wrapper
        return decorator
    
    def memoized(
        self,
        expire: Optional[Union[int, timedelta]] = None
    ) -> Callable:
        """Décorateur pour mémoïser une fonction.
        
        Args:
            expire: Durée d'expiration
            
        Returns:
            Décorateur
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Génère la clé
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
                
                # Vérifie le cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Exécute la fonction
                result = func(*args, **kwargs)
                
                # Met en cache
                self.set(cache_key, result, expire)
                
                return result
            
            return wrapper
        return decorator

# Instance globale
cache_manager = CacheManager() 