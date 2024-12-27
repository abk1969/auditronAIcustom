"""Tests de performance pour le déploiement local."""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import matplotlib.pyplot as plt

class PerformanceTests:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.results: Dict[str, List[float]] = {}
        self.concurrent_users = [1, 5, 10, 20, 50]
        self.test_duration = 60  # secondes

    async def measure_response_time(self, session, endpoint: str) -> float:
        start_time = time.time()
        async with session.get(f"{self.backend_url}{endpoint}") as response:
            await response.text()
        return time.time() - start_time

    async def simulate_user(self, session, endpoint: str):
        while True:
            try:
                response_time = await self.measure_response_time(session, endpoint)
                self.results[endpoint].append(response_time)
            except Exception as e:
                print(f"Error: {str(e)}")
            await asyncio.sleep(1)

    async def run_load_test(self, endpoint: str, num_users: int):
        self.results[endpoint] = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.simulate_user(session, endpoint) for _ in range(num_users)]
            await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

    def generate_report(self, endpoint: str):
        times = self.results[endpoint]
        if not times:
            return

        stats = {
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "p95": statistics.quantiles(times, n=20)[18],  # 95th percentile
            "p99": statistics.quantiles(times, n=100)[98]  # 99th percentile
        }

        print(f"\nPerformance stats for {endpoint}:")
        print(f"Minimum response time: {stats['min']:.3f}s")
        print(f"Maximum response time: {stats['max']:.3f}s")
        print(f"Average response time: {stats['avg']:.3f}s")
        print(f"95th percentile: {stats['p95']:.3f}s")
        print(f"99th percentile: {stats['p99']:.3f}s")

        # Générer un graphique
        plt.figure(figsize=(10, 6))
        plt.hist(times, bins=50)
        plt.title(f"Response Time Distribution - {endpoint}")
        plt.xlabel("Response Time (seconds)")
        plt.ylabel("Frequency")
        plt.savefig(f"performance_report_{endpoint.replace('/', '_')}.png")
        plt.close()

    async def run_all_tests(self):
        endpoints = [
            "/health",
            "/api/v1/analyses",
            "/api/v1/metrics"
        ]

        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            for num_users in self.concurrent_users:
                print(f"Testing with {num_users} concurrent users...")
                await asyncio.wait_for(
                    self.run_load_test(endpoint, num_users),
                    timeout=self.test_duration
                )
                self.generate_report(endpoint)

if __name__ == "__main__":
    tests = PerformanceTests()
    asyncio.run(tests.run_all_tests()) 