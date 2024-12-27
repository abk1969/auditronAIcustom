"""Tests de charge pour AuditronAI."""
import asyncio
import aiohttp
import time
from typing import Dict, Any, List
import statistics
from dataclasses import dataclass
import json
from pathlib import Path

from ...core.logger import logger
from ...core.telemetry.opentelemetry_config import telemetry

@dataclass
class TestResult:
    """Résultat d'un test de performance."""
    endpoint: str
    requests: int
    success: int
    failures: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_95: float
    requests_per_second: float

class LoadTester:
    """Testeur de charge."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialise le testeur de charge.
        
        Args:
            base_url: URL de base de l'API
        """
        self.base_url = base_url
        self.results_dir = Path("tests/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_test(
        self,
        endpoint: str,
        num_requests: int = 100,
        concurrency: int = 10,
        payload: Dict[str, Any] = None
    ) -> TestResult:
        """
        Exécute un test de charge.
        
        Args:
            endpoint: Point d'entrée à tester
            num_requests: Nombre total de requêtes
            concurrency: Nombre de requêtes simultanées
            payload: Données à envoyer
        """
        url = f"{self.base_url}{endpoint}"
        response_times: List[float] = []
        success = 0
        failures = 0
        
        semaphore = asyncio.Semaphore(concurrency)
        start_time = time.time()
        
        async def make_request():
            """Effectue une requête."""
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        request_start = time.time()
                        
                        if payload:
                            async with session.post(url, json=payload) as response:
                                await response.text()
                        else:
                            async with session.get(url) as response:
                                await response.text()
                                
                        response_time = time.time() - request_start
                        response_times.append(response_time)
                        
                        nonlocal success
                        if response.status == 200:
                            success += 1
                        else:
                            nonlocal failures
                            failures += 1
                            
                except Exception as e:
                    logger.error(f"Erreur lors du test: {e}")
                    failures += 1
        
        # Créer les tâches
        tasks = [make_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Calculer les statistiques
        result = TestResult(
            endpoint=endpoint,
            requests=num_requests,
            success=success,
            failures=failures,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            percentile_95=statistics.quantiles(response_times, n=20)[18],
            requests_per_second=num_requests / total_time
        )
        
        # Sauvegarder les résultats
        await self._save_results(result)
        
        return result
    
    async def _save_results(self, result: TestResult):
        """Sauvegarde les résultats du test."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = self.results_dir / f"load_test_{timestamp}.json"
            
            data = {
                'timestamp': timestamp,
                'endpoint': result.endpoint,
                'requests': result.requests,
                'success': result.success,
                'failures': result.failures,
                'avg_response_time': result.avg_response_time,
                'min_response_time': result.min_response_time,
                'max_response_time': result.max_response_time,
                'percentile_95': result.percentile_95,
                'requests_per_second': result.requests_per_second
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}") 