"""Outils de profilage pour le débogage."""
import cProfile
import pstats
import io
from functools import wraps
from pathlib import Path
import time
import tracemalloc
from typing import Callable, Any
import logging
from line_profiler import LineProfiler

class Profiler:
    """Classe pour le profilage des performances."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.profiler = cProfile.Profile()
        self.output_dir = Path("profiling")
        self.output_dir.mkdir(exist_ok=True)
    
    def profile(self, func: Callable) -> Callable:
        """Décorateur pour profiler une fonction."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.enabled:
                return await func(*args, **kwargs)
            
            self.profiler.enable()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                self.profiler.disable()
                output_file = self.output_dir / f"{func.__name__}_{int(time.time())}.prof"
                self.profiler.dump_stats(str(output_file))
                
                # Générer un rapport lisible
                s = io.StringIO()
                ps = pstats.Stats(self.profiler, stream=s).sort_stats("cumulative")
                ps.print_stats()
                logging.debug(f"Profile for {func.__name__}:\n{s.getvalue()}")
        
        return wrapper

class MemoryTracker:
    """Classe pour suivre l'utilisation de la mémoire."""
    
    def __init__(self):
        self.snapshot_dir = Path("memory_snapshots")
        self.snapshot_dir.mkdir(exist_ok=True)
    
    def __enter__(self):
        tracemalloc.start()
        return self
    
    def __exit__(self, *args):
        snapshot = tracemalloc.take_snapshot()
        timestamp = int(time.time())
        snapshot.dump(str(self.snapshot_dir / f"memory_{timestamp}.snap"))
        tracemalloc.stop()
    
    def compare_snapshots(self, snapshot1_path: str, snapshot2_path: str):
        """Compare deux snapshots de mémoire."""
        snapshot1 = tracemalloc.Snapshot.load(snapshot1_path)
        snapshot2 = tracemalloc.Snapshot.load(snapshot2_path)
        
        stats = snapshot2.compare_to(snapshot1, "lineno")
        return stats

def profile_lines(func: Callable) -> Any:
    """Décorateur pour profiler ligne par ligne."""
    profiler = LineProfiler()
    wrapped = profiler(func)
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await wrapped(*args, **kwargs)
        profiler.print_stats()
        return result
    
    return wrapper

# Exemple d'utilisation
profiler = Profiler()

@profiler.profile
async def expensive_function():
    # Code à profiler
    pass

@profile_lines
async def line_by_line_function():
    # Code à profiler ligne par ligne
    pass

with MemoryTracker() as tracker:
    # Code dont on veut suivre l'utilisation mémoire
    pass 