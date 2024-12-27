"""Gestionnaire d'audit de sécurité pour AuditronAI."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from .security_config import security_settings

class SecurityAuditor:
    """Gestionnaire d'audit de sécurité."""

    def __init__(self) -> None:
        """Initialise le gestionnaire d'audit."""
        self.logger = logging.getLogger("security_audit")
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure le logging de sécurité."""
        log_path = Path(security_settings.SECURITY_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def log_security_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Enregistre un événement de sécurité.
        
        Args:
            event_type: Type d'événement
            description: Description de l'événement
            severity: Niveau de sévérité
            details: Détails additionnels
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "description": description,
            "severity": severity,
            "details": details or {}
        }

        self.logger.log(
            logging.getLevelName(severity),
            json.dumps(event, indent=2)
        )

    def log_authentication_attempt(
        self,
        username: str,
        success: bool,
        ip_address: str,
        user_agent: str
    ) -> None:
        """Enregistre une tentative d'authentification.
        
        Args:
            username: Nom d'utilisateur
            success: Si la tentative a réussi
            ip_address: Adresse IP
            user_agent: User agent
        """
        details = {
            "username": username,
            "ip_address": ip_address,
            "user_agent": user_agent
        }

        self.log_security_event(
            event_type="authentication_attempt",
            description=f"Tentative d'authentification {'réussie' if success else 'échouée'} pour {username}",
            severity="INFO" if success else "WARNING",
            details=details
        )

    def log_authorization_check(
        self,
        username: str,
        resource: str,
        action: str,
        allowed: bool
    ) -> None:
        """Enregistre une vérification d'autorisation.
        
        Args:
            username: Nom d'utilisateur
            resource: Ressource accédée
            action: Action tentée
            allowed: Si l'accès a été autorisé
        """
        details = {
            "username": username,
            "resource": resource,
            "action": action
        }

        self.log_security_event(
            event_type="authorization_check",
            description=f"Vérification d'autorisation pour {username} sur {resource}",
            severity="INFO" if allowed else "WARNING",
            details=details
        )

    def log_security_violation(
        self,
        violation_type: str,
        description: str,
        ip_address: Optional[str] = None,
        username: Optional[str] = None
    ) -> None:
        """Enregistre une violation de sécurité.
        
        Args:
            violation_type: Type de violation
            description: Description de la violation
            ip_address: Adresse IP associée
            username: Nom d'utilisateur associé
        """
        details = {
            "violation_type": violation_type
        }
        if ip_address:
            details["ip_address"] = ip_address
        if username:
            details["username"] = username

        self.log_security_event(
            event_type="security_violation",
            description=description,
            severity="ERROR",
            details=details
        )

    def log_configuration_change(
        self,
        component: str,
        change_type: str,
        old_value: Any,
        new_value: Any,
        username: str
    ) -> None:
        """Enregistre un changement de configuration.
        
        Args:
            component: Composant modifié
            change_type: Type de changement
            old_value: Ancienne valeur
            new_value: Nouvelle valeur
            username: Utilisateur ayant fait le changement
        """
        details = {
            "component": component,
            "change_type": change_type,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "username": username
        }

        self.log_security_event(
            event_type="configuration_change",
            description=f"Modification de configuration sur {component}",
            severity="INFO",
            details=details
        )

    def get_recent_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère les événements récents.
        
        Args:
            event_type: Filtrer par type d'événement
            severity: Filtrer par sévérité
            limit: Nombre maximum d'événements
            
        Returns:
            Liste des événements
        """
        events = []
        try:
            with open(security_settings.SECURITY_LOG_PATH, "r") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        if event_type and event["event_type"] != event_type:
                            continue
                        if severity and event["severity"] != severity:
                            continue
                        events.append(event)
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        return events

# Instance globale de l'auditeur
security_auditor = SecurityAuditor() 