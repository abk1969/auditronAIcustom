"""Gestionnaire d'audit de sécurité."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class SecurityAuditor:
    """Gestionnaire d'audit de sécurité."""
    
    def __init__(self, log_path: Optional[Path] = None):
        """Initialise le gestionnaire.
        
        Args:
            log_path: Chemin du fichier de log
        """
        self.log_path = log_path or Path("logs/security.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """Enregistre un événement de sécurité.
        
        Args:
            event_type: Type d'événement
            user_id: ID de l'utilisateur
            details: Détails de l'événement
            success: Succès de l'événement
        """
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "user_id": str(user_id) if user_id else None,
                "success": success,
                "details": details or {}
            }
            
            with self.log_path.open("a") as f:
                json.dump(event, f)
                f.write("\n")
                
        except Exception as e:
            logger.error(
                "Erreur lors de l'enregistrement de l'événement",
                extra={
                    "event_type": event_type,
                    "user_id": str(user_id) if user_id else None,
                    "error": str(e)
                }
            )
    
    def log_auth_attempt(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Enregistre une tentative d'authentification.
        
        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur
            success: Succès de la tentative
            ip_address: Adresse IP
            user_agent: User-Agent
        """
        self.log_event(
            event_type="auth_attempt",
            user_id=user_id,
            details={
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent
            },
            success=success
        )
    
    def log_password_change(
        self,
        user_id: UUID,
        success: bool = True,
        ip_address: Optional[str] = None
    ) -> None:
        """Enregistre un changement de mot de passe.
        
        Args:
            user_id: ID de l'utilisateur
            success: Succès du changement
            ip_address: Adresse IP
        """
        self.log_event(
            event_type="password_change",
            user_id=user_id,
            details={"ip_address": ip_address},
            success=success
        )
    
    def log_password_reset(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None
    ) -> None:
        """Enregistre une réinitialisation de mot de passe.
        
        Args:
            user_id: ID de l'utilisateur
            email: Email de l'utilisateur
            success: Succès de la réinitialisation
            ip_address: Adresse IP
        """
        self.log_event(
            event_type="password_reset",
            user_id=user_id,
            details={
                "email": email,
                "ip_address": ip_address
            },
            success=success
        )
    
    def log_mfa_attempt(
        self,
        user_id: UUID,
        success: bool = True,
        ip_address: Optional[str] = None
    ) -> None:
        """Enregistre une tentative MFA.
        
        Args:
            user_id: ID de l'utilisateur
            success: Succès de la tentative
            ip_address: Adresse IP
        """
        self.log_event(
            event_type="mfa_attempt",
            user_id=user_id,
            details={"ip_address": ip_address},
            success=success
        )
    
    def log_permission_check(
        self,
        user_id: UUID,
        permission: str,
        resource: Optional[str] = None,
        success: bool = True
    ) -> None:
        """Enregistre une vérification de permission.
        
        Args:
            user_id: ID de l'utilisateur
            permission: Permission vérifiée
            resource: Ressource concernée
            success: Succès de la vérification
        """
        self.log_event(
            event_type="permission_check",
            user_id=user_id,
            details={
                "permission": permission,
                "resource": resource
            },
            success=success
        )
    
    def log_role_change(
        self,
        user_id: UUID,
        role: str,
        action: str,
        admin_id: UUID
    ) -> None:
        """Enregistre un changement de rôle.
        
        Args:
            user_id: ID de l'utilisateur
            role: Rôle concerné
            action: Action effectuée
            admin_id: ID de l'administrateur
        """
        self.log_event(
            event_type="role_change",
            user_id=user_id,
            details={
                "role": role,
                "action": action,
                "admin_id": str(admin_id)
            }
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        user_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Enregistre un événement de sécurité général.
        
        Args:
            event_type: Type d'événement
            severity: Sévérité
            message: Message
            user_id: ID de l'utilisateur
            details: Détails supplémentaires
        """
        self.log_event(
            event_type=f"security_{event_type}",
            user_id=user_id,
            details={
                "severity": severity,
                "message": message,
                **(details or {})
            }
        )
    
    def get_user_events(
        self,
        user_id: UUID,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupère les événements d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            event_type: Type d'événement
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements
        """
        try:
            events = []
            with self.log_path.open() as f:
                for line in f:
                    event = json.loads(line)
                    if event["user_id"] != str(user_id):
                        continue
                        
                    if event_type and event["event_type"] != event_type:
                        continue
                        
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    if start_date and timestamp < start_date:
                        continue
                        
                    if end_date and timestamp > end_date:
                        continue
                        
                    events.append(event)
                    
            return events
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération des événements",
                extra={
                    "user_id": str(user_id),
                    "error": str(e)
                }
            )
            return []
    
    def get_security_events(
        self,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupère les événements de sécurité.
        
        Args:
            severity: Sévérité minimale
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements
        """
        try:
            events = []
            with self.log_path.open() as f:
                for line in f:
                    event = json.loads(line)
                    if not event["event_type"].startswith("security_"):
                        continue
                        
                    if severity and (
                        "severity" not in event["details"]
                        or event["details"]["severity"] != severity
                    ):
                        continue
                        
                    timestamp = datetime.fromisoformat(event["timestamp"])
                    if start_date and timestamp < start_date:
                        continue
                        
                    if end_date and timestamp > end_date:
                        continue
                        
                    events.append(event)
                    
            return events
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération des événements de sécurité",
                extra={"error": str(e)}
            )
            return []

# Instance globale
security_auditor = SecurityAuditor() 