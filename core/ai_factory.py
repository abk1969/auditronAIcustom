"""Factory pour obtenir le bon client AI selon la configuration."""
import os
import threading
from typing import Union
from .logger import logger
import psutil

class TimeoutError(Exception):
    """Erreur de timeout."""
    pass

def limit_memory(max_mem_mb: int = 1000):
    """Limite la mémoire utilisée."""
    process = psutil.Process(os.getpid())
    try:
        process.set_memory_limit(max_mem_mb * 1024 * 1024)  # En bytes
    except AttributeError:
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (max_mem_mb * 1024 * 1024, -1))
        except Exception as e:
            logger.warning(f"Impossible de limiter la mémoire: {e}")
    except Exception as e:
        logger.warning(f"Impossible de limiter la mémoire: {e}")

class TimeoutManager:
    """Gestionnaire de timeout compatible Windows."""
    def __init__(self, seconds):
        self.seconds = seconds
        self.timer = None
        self.timed_out = False

    def handle_timeout(self):
        self.timed_out = True
        raise TimeoutError("Opération trop longue")

    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self.handle_timeout)
        self.timer.start()

    def __exit__(self, *args):
        if self.timer:
            self.timer.cancel()

def get_ai_client() -> Union['OpenAIClient', 'GeminiClient']:
    """Factory pour obtenir le bon client AI."""
    # Limiter la mémoire à 1 Go
    limit_memory(1000)
    
    service = os.getenv("AI_SERVICE", "openai").lower()
    
    try:
        with TimeoutManager(30):  # Timeout de 30 secondes
            if service == "openai":
                from .openai_client import OpenAIClient
                logger.info("Utilisation du client OpenAI")
                return OpenAIClient()
                
            elif service == "google":
                from .gemini_client import GeminiClient
                logger.info("Utilisation du client Gemini")
                return GeminiClient()
                
            else:
                error_msg = f"Service AI non reconnu : {service}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
    except TimeoutError:
        error_msg = "Timeout lors de l'initialisation du client AI"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Erreur inattendue : {str(e)}"
        logger.error(error_msg)
        raise 