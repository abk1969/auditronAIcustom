"""Gestionnaire de monitoring."""

import time
import functools
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable

from prometheus_client import Counter, Gauge, Histogram, Summary
from opentelemetry import trace

class MonitoringManager:
    """Gestionnaire de monitoring."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.metrics = {}
    
    def track_database_query(
        self,
        operation: str,
        table: str,
        duration: float
    ) -> None:
        """Suit une requête de base de données.
        
        Args:
            operation: Opération effectuée
            table: Table concernée
            duration: Durée de la requête
        """
        key = f"db.{operation}.{table}"
        if key not in self.metrics:
            self.metrics[key] = {
                "count": 0,
                "total_duration": 0.0,
                "min_duration": float("inf"),
                "max_duration": 0.0
            }
            
        self.metrics[key]["count"] += 1
        self.metrics[key]["total_duration"] += duration
        self.metrics[key]["min_duration"] = min(
            self.metrics[key]["min_duration"],
            duration
        )
        self.metrics[key]["max_duration"] = max(
            self.metrics[key]["max_duration"],
            duration
        )
    
    def track_db_query(self) -> Callable:
        """Décorateur pour suivre les requêtes de base de données.
        
        Returns:
            Décorateur
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                start_time = self.get_time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = self.get_time() - start_time
                    # Extrait le nom de la table depuis le premier argument (self)
                    if args and hasattr(args[0], "model"):
                        table = args[0].model.__tablename__
                    else:
                        table = "unknown"
                    # Utilise le nom de la fonction comme opération
                    operation = func.__name__
                    self.track_database_query(operation, table, duration)
            return wrapper
        return decorator
    
    def track_error(self, error: str) -> None:
        """Suit une erreur.
        
        Args:
            error: Message d'erreur
        """
        if "errors" not in self.metrics:
            self.metrics["errors"] = {}
            
        if error not in self.metrics["errors"]:
            self.metrics["errors"][error] = 0
            
        self.metrics["errors"][error] += 1
    
    def get_time(self) -> float:
        """Récupère le temps actuel.
        
        Returns:
            Temps en secondes
        """
        return time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques.
        
        Returns:
            Métriques
        """
        return self.metrics

# Instance globale
monitoring = MonitoringManager()