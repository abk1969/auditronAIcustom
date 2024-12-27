"""Module de métriques Prometheus."""
from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any
from functools import wraps
import time

# Métriques globales
ANALYSIS_COUNTER = Counter(
    'auditronai_analyses_total',
    'Nombre total d\'analyses effectuées',
    ['status', 'type']
)

ANALYSIS_DURATION = Histogram(
    'auditronai_analysis_duration_seconds',
    'Durée des analyses',
    ['type']
)

QUEUE_SIZE = Gauge(
    'auditronai_queue_size',
    'Taille de la file d\'attente'
)

CACHE_HITS = Counter(
    'auditronai_cache_hits_total',
    'Nombre de hits du cache'
)

CACHE_MISSES = Counter(
    'auditronai_cache_misses_total',
    'Nombre de misses du cache'
)

def track_analysis(analysis_type: str):
    """Décorateur pour suivre les analyses."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                ANALYSIS_COUNTER.labels(
                    status='success',
                    type=analysis_type
                ).inc()
                return result
            except Exception as e:
                ANALYSIS_COUNTER.labels(
                    status='error',
                    type=analysis_type
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                ANALYSIS_DURATION.labels(type=analysis_type).observe(duration)
        return wrapper
    return decorator 