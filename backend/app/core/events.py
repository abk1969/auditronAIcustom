"""Gestionnaire d'événements."""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
from uuid import UUID, uuid4
import threading
from queue import Queue
import logging

from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class Event:
    """Événement du système."""
    
    type: str
    data: Dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    correlation_id: Optional[UUID] = None

class EventBus:
    """Bus d'événements."""
    
    def __init__(self) -> None:
        """Initialise le bus d'événements."""
        self._handlers: Dict[str, List[Callable]] = {}
        self._async_handlers: Dict[str, List[Callable]] = {}
        self._queue: Queue = Queue()
        self._running = True
        self._worker = threading.Thread(target=self._process_queue)
        self._worker.daemon = True
        self._worker.start()
        
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        is_async: bool = False
    ) -> None:
        """Souscrit à un type d'événement.
        
        Args:
            event_type: Type d'événement
            handler: Gestionnaire d'événement
            is_async: Si le gestionnaire est asynchrone
        """
        if is_async:
            if event_type not in self._async_handlers:
                self._async_handlers[event_type] = []
            self._async_handlers[event_type].append(handler)
        else:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            
    def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[Event], None],
        is_async: bool = False
    ) -> None:
        """Désinscrit d'un type d'événement.
        
        Args:
            event_type: Type d'événement
            handler: Gestionnaire d'événement
            is_async: Si le gestionnaire est asynchrone
        """
        handlers = (
            self._async_handlers if is_async else self._handlers
        ).get(event_type, [])
        
        if handler in handlers:
            handlers.remove(handler)
            
    def publish(self, event: Event) -> None:
        """Publie un événement.
        
        Args:
            event: Événement à publier
        """
        self._queue.put(event)
        
    async def publish_async(self, event: Event) -> None:
        """Publie un événement de manière asynchrone.
        
        Args:
            event: Événement à publier
        """
        # Exécute les gestionnaires asynchrones
        handlers = self._async_handlers.get(event.type, [])
        await asyncio.gather(
            *[handler(event) for handler in handlers]
        )
        
        # Met l'événement dans la queue pour les gestionnaires synchrones
        self._queue.put(event)
        
    def _process_queue(self) -> None:
        """Traite la queue d'événements."""
        while self._running:
            try:
                event = self._queue.get(timeout=1.0)
                self._handle_event(event)
                self._queue.task_done()
            except Exception:
                continue
                
    def _handle_event(self, event: Event) -> None:
        """Traite un événement.
        
        Args:
            event: Événement à traiter
        """
        handlers = self._handlers.get(event.type, [])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Erreur lors du traitement de l'événement {event.type}: {e}",
                    extra={
                        "event_id": str(event.id),
                        "event_type": event.type,
                        "error": str(e)
                    }
                )
                
    def shutdown(self) -> None:
        """Arrête le bus d'événements."""
        self._running = False
        self._worker.join()
        
class EventStore:
    """Stockage d'événements."""
    
    def __init__(self) -> None:
        """Initialise le stockage d'événements."""
        self._events: List[Event] = []
        self._lock = threading.Lock()
        
    def add(self, event: Event) -> None:
        """Ajoute un événement.
        
        Args:
            event: Événement à ajouter
        """
        with self._lock:
            self._events.append(event)
            
    def get_by_type(self, event_type: str) -> List[Event]:
        """Récupère les événements par type.
        
        Args:
            event_type: Type d'événement
            
        Returns:
            Liste des événements
        """
        with self._lock:
            return [e for e in self._events if e.type == event_type]
            
    def get_by_correlation_id(self, correlation_id: UUID) -> List[Event]:
        """Récupère les événements par ID de corrélation.
        
        Args:
            correlation_id: ID de corrélation
            
        Returns:
            Liste des événements
        """
        with self._lock:
            return [
                e for e in self._events
                if e.correlation_id == correlation_id
            ]
            
    def get_by_source(self, source: str) -> List[Event]:
        """Récupère les événements par source.
        
        Args:
            source: Source des événements
            
        Returns:
            Liste des événements
        """
        with self._lock:
            return [e for e in self._events if e.source == source]
            
    def get_by_timerange(
        self,
        start: datetime,
        end: datetime
    ) -> List[Event]:
        """Récupère les événements par plage de temps.
        
        Args:
            start: Date de début
            end: Date de fin
            
        Returns:
            Liste des événements
        """
        with self._lock:
            return [
                e for e in self._events
                if start <= e.timestamp <= end
            ]
            
    def clear(self) -> None:
        """Efface tous les événements."""
        with self._lock:
            self._events.clear()

# Instances globales
event_bus = EventBus()
event_store = EventStore()

def handle_event(event_type: str, is_async: bool = False):
    """Décorateur pour gérer un type d'événement.
    
    Args:
        event_type: Type d'événement
        is_async: Si le gestionnaire est asynchrone
    """
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func, is_async)
        return func
    return decorator 