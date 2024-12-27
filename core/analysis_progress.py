"""Gestion de la progression des analyses."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .logger import logger

@dataclass
class ProgressState:
    """État de la progression."""
    total_steps: int = 0
    current_step: int = 0
    status: str = ""
    details: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sub_tasks: List['ProgressState'] = field(default_factory=list)

    @property
    def progress_percentage(self) -> float:
        """Calcule le pourcentage de progression."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100

    @property
    def elapsed_time(self) -> float:
        """Calcule le temps écoulé en secondes."""
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()

    @property
    def is_complete(self) -> bool:
        """Vérifie si la tâche est terminée."""
        return self.current_step >= self.total_steps

    @property
    def has_error(self) -> bool:
        """Vérifie si une erreur s'est produite."""
        return self.error is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'état en dictionnaire."""
        return {
            'total_steps': self.total_steps,
            'current_step': self.current_step,
            'progress_percentage': self.progress_percentage,
            'status': self.status,
            'details': self.details,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'elapsed_time': self.elapsed_time,
            'error': self.error,
            'metadata': self.metadata,
            'sub_tasks': [task.to_dict() for task in self.sub_tasks]
        }

class ProgressHandler(ABC):
    """Interface de base pour les gestionnaires de progression."""

    @abstractmethod
    def setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        pass

    @abstractmethod
    def update_progress(self, percentage: float) -> None:
        """
        Met à jour la progression.
        
        Args:
            percentage: Pourcentage de progression (0-100)
        """
        pass

    @abstractmethod
    def update_status(self, status: str) -> None:
        """
        Met à jour le statut.
        
        Args:
            status: Nouveau statut
        """
        pass

    @abstractmethod
    def update_details(self, details: str) -> None:
        """
        Met à jour les détails.
        
        Args:
            details: Nouveaux détails
        """
        pass

    @abstractmethod
    def add_sub_task(self, name: str, total_steps: int) -> 'ProgressHandler':
        """
        Ajoute une sous-tâche.
        
        Args:
            name: Nom de la sous-tâche
            total_steps: Nombre total d'étapes
            
        Returns:
            Gestionnaire pour la sous-tâche
        """
        pass

    @abstractmethod
    def complete(self) -> None:
        """Marque la tâche comme terminée."""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """
        Signale une erreur.
        
        Args:
            message: Message d'erreur
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Nettoie les ressources."""
        pass

class DefaultProgressHandler(ProgressHandler):
    """Implémentation par défaut du gestionnaire de progression."""

    def __init__(self, name: str = "main"):
        """
        Initialise le gestionnaire.
        
        Args:
            name: Nom de la tâche
        """
        self.name = name
        self.state = ProgressState()
        self.parent: Optional[DefaultProgressHandler] = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    def setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        logger.info(f"Starting task: {self.name}")

    def update_progress(self, percentage: float) -> None:
        """
        Met à jour la progression.
        
        Args:
            percentage: Pourcentage de progression (0-100)
        """
        self.state.current_step = int(percentage * self.state.total_steps / 100)
        self._log_progress()

    def update_status(self, status: str) -> None:
        """
        Met à jour le statut.
        
        Args:
            status: Nouveau statut
        """
        self.state.status = status
        logger.info(f"[{self.name}] {status}")

    def update_details(self, details: str) -> None:
        """
        Met à jour les détails.
        
        Args:
            details: Nouveaux détails
        """
        self.state.details = details
        logger.debug(f"[{self.name}] {details}")

    def add_sub_task(self, name: str, total_steps: int) -> 'DefaultProgressHandler':
        """
        Ajoute une sous-tâche.
        
        Args:
            name: Nom de la sous-tâche
            total_steps: Nombre total d'étapes
            
        Returns:
            Gestionnaire pour la sous-tâche
        """
        sub_task = DefaultProgressHandler(name)
        sub_task.state.total_steps = total_steps
        sub_task.parent = self
        self.state.sub_tasks.append(sub_task.state)
        return sub_task

    def complete(self) -> None:
        """Marque la tâche comme terminée."""
        self.state.current_step = self.state.total_steps
        self.state.completed_at = datetime.now()
        logger.info(
            f"Task completed: {self.name} "
            f"(elapsed: {self.state.elapsed_time:.2f}s)"
        )

    def error(self, message: str) -> None:
        """
        Signale une erreur.
        
        Args:
            message: Message d'erreur
        """
        self.state.error = message
        logger.error(f"[{self.name}] Error: {message}")

    def cleanup(self) -> None:
        """Nettoie les ressources."""
        self._executor.shutdown(wait=False)

    def _log_progress(self) -> None:
        """Journalise la progression."""
        logger.debug(
            f"[{self.name}] Progress: {self.state.progress_percentage:.1f}% "
            f"({self.state.current_step}/{self.state.total_steps})"
        )

class AsyncProgressHandler(ProgressHandler):
    """Gestionnaire de progression asynchrone."""

    def __init__(self, name: str = "main"):
        """
        Initialise le gestionnaire.
        
        Args:
            name: Nom de la tâche
        """
        self.name = name
        self.state = ProgressState()
        self.parent: Optional[AsyncProgressHandler] = None
        self._update_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._running = True
        self._update_task: Optional[asyncio.Task] = None

    async def setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        logger.info(f"Starting task: {self.name}")
        self._update_task = asyncio.create_task(self._process_updates())

    async def update_progress(self, percentage: float) -> None:
        """
        Met à jour la progression.
        
        Args:
            percentage: Pourcentage de progression (0-100)
        """
        await self._update_queue.put({
            'type': 'progress',
            'value': percentage
        })

    async def update_status(self, status: str) -> None:
        """
        Met à jour le statut.
        
        Args:
            status: Nouveau statut
        """
        await self._update_queue.put({
            'type': 'status',
            'value': status
        })

    async def update_details(self, details: str) -> None:
        """
        Met à jour les détails.
        
        Args:
            details: Nouveaux détails
        """
        await self._update_queue.put({
            'type': 'details',
            'value': details
        })

    def add_sub_task(self, name: str, total_steps: int) -> 'AsyncProgressHandler':
        """
        Ajoute une sous-tâche.
        
        Args:
            name: Nom de la sous-tâche
            total_steps: Nombre total d'étapes
            
        Returns:
            Gestionnaire pour la sous-tâche
        """
        sub_task = AsyncProgressHandler(name)
        sub_task.state.total_steps = total_steps
        sub_task.parent = self
        self.state.sub_tasks.append(sub_task.state)
        return sub_task

    async def complete(self) -> None:
        """Marque la tâche comme terminée."""
        await self._update_queue.put({
            'type': 'complete'
        })

    async def error(self, message: str) -> None:
        """
        Signale une erreur.
        
        Args:
            message: Message d'erreur
        """
        await self._update_queue.put({
            'type': 'error',
            'value': message
        })

    async def cleanup(self) -> None:
        """Nettoie les ressources."""
        self._running = False
        if self._update_task:
            await self._update_task

    async def _process_updates(self) -> None:
        """Traite les mises à jour de progression."""
        while self._running:
            try:
                update = await self._update_queue.get()
                update_type = update['type']

                if update_type == 'progress':
                    percentage = update['value']
                    self.state.current_step = int(
                        percentage * self.state.total_steps / 100
                    )
                    self._log_progress()

                elif update_type == 'status':
                    self.state.status = update['value']
                    logger.info(f"[{self.name}] {self.state.status}")

                elif update_type == 'details':
                    self.state.details = update['value']
                    logger.debug(f"[{self.name}] {self.state.details}")

                elif update_type == 'complete':
                    self.state.current_step = self.state.total_steps
                    self.state.completed_at = datetime.now()
                    logger.info(
                        f"Task completed: {self.name} "
                        f"(elapsed: {self.state.elapsed_time:.2f}s)"
                    )

                elif update_type == 'error':
                    self.state.error = update['value']
                    logger.error(f"[{self.name}] Error: {self.state.error}")

                self._update_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing progress update: {str(e)}")

    def _log_progress(self) -> None:
        """Journalise la progression."""
        logger.debug(
            f"[{self.name}] Progress: {self.state.progress_percentage:.1f}% "
            f"({self.state.current_step}/{self.state.total_steps})"
        )
