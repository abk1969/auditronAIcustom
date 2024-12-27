"""Worker pour l'analyse parallèle."""
import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import multiprocessing as mp

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry
from ..cache.redis_cache import RedisCache
from ..security_analyzer import SecurityAnalyzer

@dataclass
class AnalysisTask:
    """Tâche d'analyse."""
    id: str
    code: str
    options: Dict[str, Any]
    priority: int = 0

class AnalysisWorkerPool:
    """Pool de workers pour l'analyse parallèle."""
    
    def __init__(self, num_workers: Optional[int] = None):
        """
        Initialise le pool de workers.
        
        Args:
            num_workers: Nombre de workers (défaut: nombre de CPUs)
        """
        self.num_workers = num_workers or mp.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.num_workers)
        self.cache = RedisCache(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379))
        )
        self.tasks: asyncio.PriorityQueue[AnalysisTask] = asyncio.PriorityQueue()
        self.running = False
        self.workers: List[asyncio.Task] = []
    
    @telemetry.trace_method("analyze_code")
    async def analyze_code(self, task: AnalysisTask) -> Dict[str, Any]:
        """
        Analyse un code source.
        
        Args:
            task: Tâche d'analyse
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            # Vérifier le cache
            cache_key = f"analysis:{task.id}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Résultat trouvé dans le cache pour {task.id}")
                return cached_result
            
            # Analyser le code
            loop = asyncio.get_event_loop()
            analyzer = SecurityAnalyzer()
            result = await loop.run_in_executor(
                self.executor,
                analyzer.analyze,
                task.code,
                task.options
            )
            
            # Mettre en cache
            self.cache.set(cache_key, result, ttl=3600)  # 1 heure
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse {task.id}: {e}")
            raise
    
    async def start(self):
        """Démarre les workers."""
        self.running = True
        
        for _ in range(self.num_workers):
            worker = asyncio.create_task(self._worker_loop())
            self.workers.append(worker)
            
        logger.info(f"{self.num_workers} workers démarrés")
    
    async def stop(self):
        """Arrête les workers."""
        self.running = False
        
        for worker in self.workers:
            worker.cancel()
            
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        self.executor.shutdown()
        
        logger.info("Workers arrêtés")
    
    async def _worker_loop(self):
        """Boucle principale d'un worker."""
        while self.running:
            try:
                task = await self.tasks.get()
                
                try:
                    result = await self.analyze_code(task)
                    logger.info(f"Analyse {task.id} terminée")
                    
                except Exception as e:
                    logger.error(f"Erreur dans le worker: {e}")
                    
                finally:
                    self.tasks.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle worker: {e}")
                await asyncio.sleep(1) 