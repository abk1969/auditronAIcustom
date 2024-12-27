"""Gestionnaire de monitoring."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from prometheus_client import Counter, Gauge, Histogram, Summary
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from app.core.logging import get_logger

logger = get_logger(__name__)

class MonitoringManager:
    """Gestionnaire de monitoring."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        # Métriques Prometheus
        self.http_requests_total = Counter(
            "http_requests_total",
            "Nombre total de requêtes HTTP",
            ["method", "endpoint", "status"]
        )
        
        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "Durée des requêtes HTTP",
            ["method", "endpoint"]
        )
        
        self.active_users = Gauge(
            "active_users",
            "Nombre d'utilisateurs actifs"
        )
        
        self.database_queries_total = Counter(
            "database_queries_total",
            "Nombre total de requêtes de base de données",
            ["operation", "table"]
        )
        
        self.database_query_duration_seconds = Histogram(
            "database_query_duration_seconds",
            "Durée des requêtes de base de données",
            ["operation", "table"]
        )
        
        self.cache_hits_total = Counter(
            "cache_hits_total",
            "Nombre total de hits du cache",
            ["cache_type"]
        )
        
        self.cache_misses_total = Counter(
            "cache_misses_total",
            "Nombre total de misses du cache",
            ["cache_type"]
        )
        
        self.task_duration_seconds = Histogram(
            "task_duration_seconds",
            "Durée des tâches asynchrones",
            ["task_name"]
        )
        
        self.errors_total = Counter(
            "errors_total",
            "Nombre total d'erreurs",
            ["type", "location"]
        )
        
        self.memory_usage_bytes = Gauge(
            "memory_usage_bytes",
            "Utilisation de la mémoire en bytes"
        )
        
        self.cpu_usage_percent = Gauge(
            "cpu_usage_percent",
            "Utilisation du CPU en pourcentage"
        )
        
        # Tracer OpenTelemetry
        self.tracer = trace.get_tracer(__name__)
    
    def track_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ) -> None:
        """Suit une requête HTTP.
        
        Args:
            method: Méthode HTTP
            endpoint: Point de terminaison
            status: Code de statut
            duration: Durée en secondes
        """
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def track_database_query(
        self,
        operation: str,
        table: str,
        duration: float
    ) -> None:
        """Suit une requête de base de données.
        
        Args:
            operation: Type d'opération
            table: Table concernée
            duration: Durée en secondes
        """
        self.database_queries_total.labels(
            operation=operation,
            table=table
        ).inc()
        
        self.database_query_duration_seconds.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def track_cache(
        self,
        cache_type: str,
        hit: bool,
        size: Optional[int] = None
    ) -> None:
        """Suit une opération de cache.
        
        Args:
            cache_type: Type de cache
            hit: True si hit, False si miss
            size: Taille des données
        """
        if hit:
            self.cache_hits_total.labels(
                cache_type=cache_type
            ).inc()
        else:
            self.cache_misses_total.labels(
                cache_type=cache_type
            ).inc()
    
    def track_task(self, task_name: str, duration: float) -> None:
        """Suit une tâche asynchrone.
        
        Args:
            task_name: Nom de la tâche
            duration: Durée en secondes
        """
        self.task_duration_seconds.labels(
            task_name=task_name
        ).observe(duration)
    
    def track_error(self, error_type: str, location: str) -> None:
        """Suit une erreur.
        
        Args:
            error_type: Type d'erreur
            location: Emplacement de l'erreur
        """
        self.errors_total.labels(
            type=error_type,
            location=location
        ).inc()
    
    def track_memory(self, bytes_used: int) -> None:
        """Suit l'utilisation de la mémoire.
        
        Args:
            bytes_used: Bytes utilisés
        """
        self.memory_usage_bytes.set(bytes_used)
    
    def track_cpu(self, percent_used: float) -> None:
        """Suit l'utilisation du CPU.
        
        Args:
            percent_used: Pourcentage utilisé
        """
        self.cpu_usage_percent.set(percent_used)
    
    def create_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Crée un span de traçage.
        
        Args:
            name: Nom du span
            attributes: Attributs du span
            
        Returns:
            Span créé
        """
        return self.tracer.start_span(
            name=name,
            attributes=attributes
        )
    
    def end_span(
        self,
        span: Any,
        status: Optional[Union[Status, StatusCode]] = None
    ) -> None:
        """Termine un span de traçage.
        
        Args:
            span: Span à terminer
            status: Statut final
        """
        if status:
            span.set_status(status)
        span.end()
    
    def add_span_event(
        self,
        span: Any,
        name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Ajoute un événement à un span.
        
        Args:
            span: Span concerné
            name: Nom de l'événement
            attributes: Attributs de l'événement
        """
        span.add_event(
            name=name,
            attributes=attributes
        )

# Instance globale
monitoring = MonitoringManager() 