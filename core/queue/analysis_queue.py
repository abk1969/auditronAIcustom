"""Gestionnaire de file d'attente pour les analyses."""
import asyncio
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime
from ..logger import logger

class AnalysisQueue:
    """File d'attente pour les analyses de code."""
    
    def __init__(self, max_concurrent: int = 5):
        """
        Initialise la file d'attente.
        
        Args:
            max_concurrent: Nombre maximum d'analyses simultanées
        """
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.running = False
        self._workers = []

    async def enqueue(self, analysis_data: Dict[str, Any]) -> str:
        """
        Ajoute une analyse à la file d'attente.
        
        Args:
            analysis_data: Données de l'analyse
            
        Returns:
            str: ID de l'analyse
        """
        analysis_id = f"analysis_{datetime.now().timestamp()}"
        await self.queue.put({
            'id': analysis_id,
            'data': analysis_data,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        })
        logger.info(f"Analyse {analysis_id} ajoutée à la file d'attente")
        return analysis_id

    async def process_queue(self, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        """
        Traite la file d'attente.
        
        Args:
            handler: Fonction de traitement des analyses
        """
        self.running = True
        
        while self.running:
            try:
                async with self.semaphore:
                    analysis = await self.queue.get()
                    
                    try:
                        logger.info(f"Traitement de l'analyse {analysis['id']}")
                        result = await handler(analysis['data'])
                        analysis['status'] = 'completed'
                        analysis['result'] = result
                        
                    except Exception as e:
                        logger.error(f"Erreur lors de l'analyse {analysis['id']}: {e}")
                        analysis['status'] = 'error'
                        analysis['error'] = str(e)
                        
                    finally:
                        self.queue.task_done()
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la file d'attente: {e}")
                await asyncio.sleep(1)

    def start(self, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]], num_workers: int = 3):
        """
        Démarre les workers de la file d'attente.
        
        Args:
            handler: Fonction de traitement
            num_workers: Nombre de workers
        """
        for _ in range(num_workers):
            worker = asyncio.create_task(self.process_queue(handler))
            self._workers.append(worker)
        logger.info(f"{num_workers} workers démarrés")

    async def stop(self):
        """Arrête la file d'attente."""
        self.running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("File d'attente arrêtée") 