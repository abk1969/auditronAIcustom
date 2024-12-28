"""Gestionnaire de tâches asynchrones."""

from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.core.monitoring import monitoring

logger = get_logger(__name__)

# Création de l'application Celery
celery_app = Celery(
    "auditronai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 heure
    task_soft_time_limit=3300,  # 55 minutes
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=4
)

# Tâches périodiques
celery_app.conf.beat_schedule = {
    "cleanup-expired-sessions": {
        "task": "app.tasks.auth.cleanup_expired_sessions",
        "schedule": crontab(minute=0, hour="*/1")  # Toutes les heures
    },
    "backup-database": {
        "task": "app.tasks.maintenance.backup_database",
        "schedule": crontab(minute=0, hour=0)  # Minuit
    },
    "update-metrics": {
        "task": "app.tasks.monitoring.update_metrics",
        "schedule": 60.0  # Toutes les minutes
    }
}

class TaskManager:
    """Gestionnaire de tâches."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.app = celery_app
    
    def send_task(
        self,
        name: str,
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        countdown: Optional[int] = None,
        eta: Optional[Any] = None,
        expires: Optional[Any] = None,
        retry: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        queue: Optional[str] = None
    ) -> AsyncResult:
        """Envoie une tâche.
        
        Args:
            name: Nom de la tâche
            args: Arguments positionnels
            kwargs: Arguments nommés
            countdown: Délai avant exécution
            eta: Date d'exécution
            expires: Date d'expiration
            retry: Autoriser les réessais
            retry_policy: Politique de réessai
            queue: File d'attente
            
        Returns:
            Résultat asynchrone
        """
        try:
            return self.app.send_task(
                name,
                args=args,
                kwargs=kwargs,
                countdown=countdown,
                eta=eta,
                expires=expires,
                retry=retry,
                retry_policy=retry_policy,
                queue=queue
            )
        except Exception as e:
            logger.error(
                "Erreur lors de l'envoi de la tâche",
                extra={
                    "error": str(e),
                    "task": name,
                    "args": args,
                    "kwargs": kwargs
                }
            )
            raise
    
    def get_task_result(self, task_id: str) -> AsyncResult:
        """Récupère le résultat d'une tâche.
        
        Args:
            task_id: ID de la tâche
            
        Returns:
            Résultat asynchrone
        """
        return AsyncResult(task_id, app=self.app)
    
    def revoke_task(
        self,
        task_id: str,
        terminate: bool = False,
        signal: Optional[str] = None
    ) -> None:
        """Annule une tâche.
        
        Args:
            task_id: ID de la tâche
            terminate: Terminer la tâche en cours
            signal: Signal à envoyer
        """
        try:
            self.app.control.revoke(
                task_id,
                terminate=terminate,
                signal=signal
            )
        except Exception as e:
            logger.error(
                "Erreur lors de l'annulation de la tâche",
                extra={
                    "error": str(e),
                    "task_id": task_id
                }
            )
            raise
    
    def get_active_tasks(self) -> list[Dict[str, Any]]:
        """Récupère les tâches actives.
        
        Returns:
            Liste des tâches actives
        """
        try:
            active = self.app.control.inspect().active()
            if not active:
                return []
            
            tasks = []
            for worker in active.values():
                tasks.extend(worker)
            
            return tasks
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération des tâches actives",
                extra={"error": str(e)}
            )
            return []
    
    def get_scheduled_tasks(self) -> list[Dict[str, Any]]:
        """Récupère les tâches planifiées.
        
        Returns:
            Liste des tâches planifiées
        """
        try:
            scheduled = self.app.control.inspect().scheduled()
            if not scheduled:
                return []
            
            tasks = []
            for worker in scheduled.values():
                tasks.extend(worker)
            
            return tasks
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération des tâches planifiées",
                extra={"error": str(e)}
            )
            return []
    
    def get_reserved_tasks(self) -> list[Dict[str, Any]]:
        """Récupère les tâches réservées.
        
        Returns:
            Liste des tâches réservées
        """
        try:
            reserved = self.app.control.inspect().reserved()
            if not reserved:
                return []
            
            tasks = []
            for worker in reserved.values():
                tasks.extend(worker)
            
            return tasks
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération des tâches réservées",
                extra={"error": str(e)}
            )
            return []

# Instance globale
task_manager = TaskManager() 