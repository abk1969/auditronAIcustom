"""Gestionnaire de ressources système."""
import psutil
import os
from typing import Dict, Optional
from dataclasses import dataclass
from .logger import logger

@dataclass
class ResourceQuota:
    """Quota de ressources."""
    max_memory_mb: int
    max_cpu_percent: float
    max_disk_mb: int

class ResourceManager:
    """Gère les ressources système."""
    
    def __init__(self):
        """Initialise le gestionnaire de ressources."""
        self.quotas: Dict[str, ResourceQuota] = {
            'analysis': ResourceQuota(
                max_memory_mb=500,
                max_cpu_percent=50.0,
                max_disk_mb=1000
            ),
            'ai': ResourceQuota(
                max_memory_mb=1000,
                max_cpu_percent=75.0,
                max_disk_mb=2000
            )
        }
        self.process = psutil.Process(os.getpid())

    def check_resources(self, quota_type: str) -> bool:
        """
        Vérifie si les ressources sont disponibles.
        
        Args:
            quota_type: Type de quota à vérifier
            
        Returns:
            bool: True si les ressources sont disponibles
        """
        try:
            quota = self.quotas[quota_type]
            
            # Vérifier la mémoire
            memory_usage = self.process.memory_info().rss / (1024 * 1024)  # MB
            if memory_usage > quota.max_memory_mb:
                logger.warning(f"Limite de mémoire dépassée: {memory_usage}MB")
                return False
            
            # Vérifier le CPU
            cpu_percent = self.process.cpu_percent()
            if cpu_percent > quota.max_cpu_percent:
                logger.warning(f"Limite de CPU dépassée: {cpu_percent}%")
                return False
            
            # Vérifier l'espace disque
            disk_usage = psutil.disk_usage('/').used / (1024 * 1024)  # MB
            if disk_usage > quota.max_disk_mb:
                logger.warning(f"Limite de disque dépassée: {disk_usage}MB")
                return False
            
            return True
            
        except KeyError:
            logger.error(f"Type de quota inconnu: {quota_type}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des ressources: {e}")
            return False

    def get_resource_usage(self) -> Dict[str, float]:
        """Retourne l'utilisation actuelle des ressources."""
        try:
            return {
                'memory_mb': self.process.memory_info().rss / (1024 * 1024),
                'cpu_percent': self.process.cpu_percent(),
                'disk_mb': psutil.disk_usage('/').used / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisation des ressources: {e}")
            return {}

    def cleanup_resources(self):
        """Nettoie les ressources inutilisées."""
        try:
            # Forcer le garbage collector
            import gc
            gc.collect()
            
            # Vider le cache de mémoire
            if hasattr(os, 'sync'):
                os.sync()
                
            logger.info("Nettoyage des ressources effectué")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des ressources: {e}") 