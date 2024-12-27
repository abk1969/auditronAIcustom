"""Tests de performance pour les analyses."""
import pytest
import asyncio
import time
from typing import List
from app.models.analysis import Analysis, AnalysisStatus
from app.cqrs.analysis import CreateAnalysisCommand, CreateAnalysisHandler

@pytest.mark.performance
class TestAnalysisPerformance:
    async def test_concurrent_analysis_creation(
        self, 
        create_analysis_handler: CreateAnalysisHandler,
        db_session
    ):
        start_time = time.time()
        num_requests = 100
        
        async def create_single_analysis(i: int):
            command = CreateAnalysisCommand(
                user_id="test_user",
                code_snippet=f"print('test_{i}')",
                language="python"
            )
            return await create_analysis_handler.handle(command)
        
        # Exécuter les créations en parallèle
        tasks = [create_single_analysis(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifications
        assert len(results) == num_requests
        assert all(isinstance(r, Analysis) for r in results)
        assert duration < 5.0  # La création de 100 analyses doit prendre moins de 5 secondes

    async def test_analysis_memory_usage(
        self, 
        create_analysis_handler: CreateAnalysisHandler,
        db_session
    ):
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Créer 1000 analyses
        for i in range(1000):
            command = CreateAnalysisCommand(
                user_id="test_user",
                code_snippet="print('hello')" * 100,  # Code plus long
                language="python"
            )
            await create_analysis_handler.handle(command)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # En MB
        
        # L'augmentation de mémoire ne doit pas dépasser 100MB
        assert memory_increase < 100 