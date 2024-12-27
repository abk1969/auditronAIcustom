"""Module de limitation de débit."""
import time
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from .logger import logger

@dataclass
class RateLimit:
    """Configuration d'une limite de débit."""
    requests: int  # Nombre de requêtes autorisées
    window: int   # Fenêtre de temps en secondes
    
class RateLimiter:
    """Gestionnaire de limitation de débit."""
    
    def __init__(self):
        """Initialise le rate limiter."""
        self.limits: Dict[str, RateLimit] = {
            'default': RateLimit(100, 3600),  # 100 requêtes/heure par défaut
            'analysis': RateLimit(10, 60),    # 10 analyses/minute
            'ai': RateLimit(50, 3600),        # 50 requêtes AI/heure
        }
        self.counters: Dict[str, Dict[str, int]] = {}
        self.timestamps: Dict[str, Dict[str, float]] = {}

    async def check_rate_limit(self, key: str, limit_type: str = 'default') -> bool:
        """
        Vérifie si une requête est autorisée.
        
        Args:
            key: Identifiant du client
            limit_type: Type de limite à vérifier
            
        Returns:
            bool: True si la requête est autorisée
        """
        try:
            limit = self.limits[limit_type]
            now = time.time()
            
            # Initialiser les compteurs si nécessaire
            if key not in self.counters:
                self.counters[key] = {}
                self.timestamps[key] = {}
            
            if limit_type not in self.counters[key]:
                self.counters[key][limit_type] = 0
                self.timestamps[key][limit_type] = now
            
            # Vérifier si la fenêtre est expirée
            window_start = self.timestamps[key][limit_type]
            if now - window_start > limit.window:
                self.counters[key][limit_type] = 0
                self.timestamps[key][limit_type] = now
            
            # Vérifier la limite
            if self.counters[key][limit_type] >= limit.requests:
                logger.warning(f"Rate limit dépassé pour {key} ({limit_type})")
                return False
            
            # Incrémenter le compteur
            self.counters[key][limit_type] += 1
            return True
            
        except KeyError:
            logger.error(f"Type de limite inconnu: {limit_type}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du rate limit: {e}")
            return False

    def get_remaining(self, key: str, limit_type: str = 'default') -> Optional[int]:
        """Retourne le nombre de requêtes restantes."""
        try:
            limit = self.limits[limit_type]
            if key in self.counters and limit_type in self.counters[key]:
                return max(0, limit.requests - self.counters[key][limit_type])
            return limit.requests
        except Exception as e:
            logger.error(f"Erreur lors du calcul des requêtes restantes: {e}")
            return None

    def get_reset_time(self, key: str, limit_type: str = 'default') -> Optional[datetime]:
        """Retourne le temps avant réinitialisation."""
        try:
            if key in self.timestamps and limit_type in self.timestamps[key]:
                window_end = self.timestamps[key][limit_type] + self.limits[limit_type].window
                return datetime.fromtimestamp(window_end)
            return None
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de réinitialisation: {e}")
            return None 