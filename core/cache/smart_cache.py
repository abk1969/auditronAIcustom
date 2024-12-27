"""Cache intelligent avec prédiction d'expiration."""
from typing import Dict, Any, Optional, List, Tuple
import time
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
import pickle
import json

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry
from .redis_cache import RedisCache

@dataclass
class CacheStats:
    """Statistiques d'utilisation du cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_latency: float = 0.0
    access_count: Dict[str, int] = None
    
    def __post_init__(self):
        """Initialise le compteur d'accès."""
        if self.access_count is None:
            self.access_count = {}

class SmartCache:
    """Cache intelligent avec prédiction d'expiration."""
    
    def __init__(self, redis_cache: RedisCache, max_size: int = 1000):
        """
        Initialise le cache intelligent.
        
        Args:
            redis_cache: Instance du cache Redis
            max_size: Taille maximale du cache
        """
        self.redis = redis_cache
        self.max_size = max_size
        self.stats = CacheStats()
        self.access_history: List[Tuple[str, datetime]] = []
        self.prediction_model = None
        
        # Charger le modèle de prédiction
        self._load_model()
    
    def _load_model(self):
        """Charge ou initialise le modèle de prédiction."""
        try:
            model_data = self.redis.get('cache:prediction_model')
            if model_data:
                self.prediction_model = pickle.loads(model_data)
            else:
                # Modèle simple basé sur la moyenne mobile
                self.prediction_model = {
                    'window_size': 10,
                    'min_samples': 5,
                    'weights': np.ones(10) / 10  # Moyenne mobile simple
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self.prediction_model = None
    
    @telemetry.trace_method("cache_get")
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache.
        
        Args:
            key: Clé de cache
            
        Returns:
            Optional[Any]: Valeur ou None si non trouvée
        """
        start_time = time.time()
        try:
            value = self.redis.get(key)
            
            if value is not None:
                self.stats.hits += 1
                self._update_stats(key, True, start_time)
                return value
                
            self.stats.misses += 1
            self._update_stats(key, False, start_time)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du cache: {e}")
            return None
    
    @telemetry.trace_method("cache_set")
    def set(self, key: str, value: Any) -> bool:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            
        Returns:
            bool: True si succès
        """
        try:
            # Prédire le TTL
            ttl = self._predict_ttl(key)
            
            # Vérifier la taille du cache
            if len(self.stats.access_count) >= self.max_size:
                self._evict_entries()
            
            return self.redis.set(key, value, ttl=ttl)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans le cache: {e}")
            return False
    
    def _predict_ttl(self, key: str) -> int:
        """Prédit le TTL optimal pour une clé."""
        try:
            if not self.prediction_model or key not in self.stats.access_count:
                return 3600  # 1 heure par défaut
            
            # Calculer le score d'importance
            access_count = self.stats.access_count[key]
            recent_accesses = sum(1 for k, _ in self.access_history[-100:] if k == key)
            
            importance = (access_count * 0.7 + recent_accesses * 0.3) / 100
            
            # Ajuster le TTL selon l'importance
            base_ttl = 3600  # 1 heure
            min_ttl = 300    # 5 minutes
            max_ttl = 86400  # 24 heures
            
            ttl = int(base_ttl * (1 + importance))
            return max(min_ttl, min(ttl, max_ttl))
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction du TTL: {e}")
            return 3600
    
    def _evict_entries(self):
        """Supprime les entrées les moins utilisées."""
        try:
            # Trier par nombre d'accès
            sorted_entries = sorted(
                self.stats.access_count.items(),
                key=lambda x: x[1]
            )
            
            # Supprimer 10% des entrées les moins utilisées
            num_to_evict = max(1, len(sorted_entries) // 10)
            
            for key, _ in sorted_entries[:num_to_evict]:
                self.redis.delete(key)
                del self.stats.access_count[key]
                self.stats.evictions += 1
                
        except Exception as e:
            logger.error(f"Erreur lors de l'éviction: {e}")
    
    def _update_stats(self, key: str, hit: bool, start_time: float):
        """Met à jour les statistiques."""
        try:
            # Mettre à jour le compteur d'accès
            self.stats.access_count[key] = self.stats.access_count.get(key, 0) + 1
            
            # Mettre à jour l'historique
            self.access_history.append((key, datetime.now()))
            if len(self.access_history) > 1000:
                self.access_history = self.access_history[-1000:]
            
            # Mettre à jour la latence
            self.stats.total_latency += time.time() - start_time
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des stats: {e}") 