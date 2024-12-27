"""Système de métriques de performance."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import asyncio
import statistics

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

@dataclass
class SystemMetrics:
    """Métriques système."""
    cpu_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    network_io_mb: float
    process_count: int

@dataclass
class ApplicationMetrics:
    """Métriques applicatives."""
    request_count: int
    error_count: int
    avg_response_time: float
    cache_hit_rate: float
    active_connections: int

class PerformanceMonitor:
    """Moniteur de performance."""
    
    def __init__(self, sampling_interval: int = 60):
        """
        Initialise le moniteur.
        
        Args:
            sampling_interval: Intervalle d'échantillonnage en secondes
        """
        self.sampling_interval = sampling_interval
        self.metrics_history: List[Dict[str, Any]] = []
        self.running = False
        self._monitor_task = None
    
    async def start_monitoring(self):
        """Démarre la surveillance."""
        self.running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Surveillance des performances démarrée")
    
    async def stop_monitoring(self):
        """Arrête la surveillance."""
        self.running = False
        if self._monitor_task:
            await self._monitor_task
        logger.info("Surveillance des performances arrêtée")
    
    @telemetry.trace_method("collect_metrics")
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques."""
        try:
            # Métriques système
            system = SystemMetrics(
                cpu_percent=psutil.cpu_percent(),
                memory_usage_mb=psutil.Process().memory_info().rss / (1024 * 1024),
                disk_usage_percent=psutil.disk_usage('/').percent,
                network_io_mb=sum(psutil.net_io_counters()[:2]) / (1024 * 1024),
                process_count=len(psutil.Process().children())
            )
            
            # Métriques applicatives
            app = ApplicationMetrics(
                request_count=self._get_request_count(),
                error_count=self._get_error_count(),
                avg_response_time=self._calculate_avg_response_time(),
                cache_hit_rate=self._calculate_cache_hit_rate(),
                active_connections=self._get_active_connections()
            )
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': system.__dict__,
                'application': app.__dict__
            }
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques: {e}")
            return {}
    
    async def _monitoring_loop(self):
        """Boucle de surveillance."""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.sampling_interval)
            except Exception as e:
                logger.error(f"Erreur dans la boucle de surveillance: {e}")
                await asyncio.sleep(5)
    
    @telemetry.trace_method("analyze_metrics")
    def analyze_metrics(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Analyse les métriques.
        
        Args:
            time_window: Fenêtre de temps pour l'analyse
        """
        try:
            cutoff = datetime.now() - time_window
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m['timestamp']) > cutoff
            ]
            
            if not recent_metrics:
                return {}
            
            # Analyser les tendances
            cpu_trend = [m['system']['cpu_percent'] for m in recent_metrics]
            memory_trend = [m['system']['memory_usage_mb'] for m in recent_metrics]
            response_times = [m['application']['avg_response_time'] for m in recent_metrics]
            
            return {
                'system_health': {
                    'cpu': {
                        'avg': statistics.mean(cpu_trend),
                        'max': max(cpu_trend),
                        'trend': self._calculate_trend(cpu_trend)
                    },
                    'memory': {
                        'avg': statistics.mean(memory_trend),
                        'max': max(memory_trend),
                        'trend': self._calculate_trend(memory_trend)
                    }
                },
                'application_health': {
                    'response_time': {
                        'avg': statistics.mean(response_times),
                        'p95': statistics.quantiles(response_times, n=20)[18],
                        'trend': self._calculate_trend(response_times)
                    },
                    'error_rate': self._calculate_error_rate(recent_metrics),
                    'cache_efficiency': self._calculate_cache_efficiency(recent_metrics)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des métriques: {e}")
            return {}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance d'une série de valeurs."""
        if len(values) < 2:
            return "stable"
            
        start = statistics.mean(values[:len(values)//3])
        end = statistics.mean(values[-len(values)//3:])
        
        diff = end - start
        if abs(diff) < 0.1 * start:
            return "stable"
        return "increasing" if diff > 0 else "decreasing" 