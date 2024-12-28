"""Configuration du debugging."""
import sys
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps
import time
import traceback
import debugpy

def setup_remote_debugging(port: int = 5678):
    """Configure le debugging distant."""
    debugpy.listen(("0.0.0.0", port))
    print(f"⚡ Remote debugging enabled on port {port}")

def setup_debug_logging():
    """Configure les logs de debugging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    debug_handler = logging.FileHandler(
        log_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    debug_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    debug_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(debug_handler)
    root_logger.setLevel(logging.DEBUG)

def debug_endpoint(func):
    """Décorateur pour le debugging des endpoints."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.debug(
                f"Endpoint {func.__name__} completed in {execution_time:.3f}s"
            )
            return result
        except Exception as e:
            logging.error(
                f"Error in {func.__name__}: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    return wrapper 