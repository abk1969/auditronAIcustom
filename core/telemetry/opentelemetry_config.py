"""Configuration OpenTelemetry pour AuditronAI."""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from functools import wraps
from typing import Optional, Callable
import os

from ..logger import logger

class TelemetryManager:
    """Gestionnaire de télémétrie."""
    
    def __init__(self):
        """Initialise le gestionnaire de télémétrie."""
        self.tracer_provider = TracerProvider()
        self.setup_exporters()
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(__name__)
        
        # Instrumenter les bibliothèques
        self._setup_instrumentations()
    
    def setup_exporters(self):
        """Configure les exporteurs de télémétrie."""
        try:
            # Exporteur OTLP
            otlp_exporter = OTLPSpanExporter(
                endpoint=os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
            )
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            logger.info("Exporteur OTLP configuré")
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des exporteurs: {e}")
    
    def _setup_instrumentations(self):
        """Configure les instrumentations automatiques."""
        try:
            # Instrumenter Redis
            RedisInstrumentor().instrument()
            
            # Instrumenter les requêtes HTTP
            RequestsInstrumentor().instrument()
            
            logger.info("Instrumentations configurées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration des instrumentations: {e}")
    
    def trace_method(self, name: Optional[str] = None):
        """Décorateur pour tracer une méthode."""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                span_name = name or func.__name__
                with self.tracer.start_as_current_span(span_name) as span:
                    # Ajouter des attributs au span
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("module.name", func.__module__)
                    
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        span.set_attribute("error", True)
                        span.set_attribute("error.message", str(e))
                        raise
                        
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                span_name = name or func.__name__
                with self.tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("module.name", func.__module__)
                    
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        span.set_attribute("error", True)
                        span.set_attribute("error.message", str(e))
                        raise
                        
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator

# Instance globale
telemetry = TelemetryManager() 