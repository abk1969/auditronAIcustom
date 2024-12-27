"""Gestionnaire de session sécurisé pour AuditronAI."""

import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from fastapi import Request, Response
from itsdangerous import URLSafeTimedSerializer
from redis import Redis

from .security_config import security_settings
from .security_auditor import security_auditor
from .secrets_manager import secrets_manager

class SessionManager:
    """Gestionnaire de session avec stockage Redis."""

    def __init__(self) -> None:
        """Initialise le gestionnaire de session."""
        self._redis = Redis(
            host=secrets_manager.get_secret("REDIS_HOST", "localhost"),
            port=int(secrets_manager.get_secret("REDIS_PORT", "6379")),
            password=secrets_manager.get_secret("REDIS_PASSWORD"),
            ssl=security_settings.CACHE_SSL_REQUIRED,
            decode_responses=True
        )
        
        self._serializer = URLSafeTimedSerializer(
            secrets_manager.get_secret("SESSION_SECRET")
        )
        
        # Préfixe pour les clés Redis
        self._prefix = "session:"

    def create_session(
        self,
        user_id: str,
        data: Dict[str, Any],
        response: Response
    ) -> str:
        """Crée une nouvelle session.
        
        Args:
            user_id: ID de l'utilisateur
            data: Données de session
            response: Réponse HTTP pour définir le cookie
            
        Returns:
            ID de session
        """
        session_id = str(uuid.uuid4())
        expires = datetime.utcnow() + timedelta(
            seconds=security_settings.SESSION_MAX_AGE
        )
        
        # Stocke les données de session
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires.isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        self._redis.setex(
            f"{self._prefix}{session_id}",
            security_settings.SESSION_MAX_AGE,
            self._serializer.dumps(session_data)
        )
        
        # Définit le cookie de session
        self._set_session_cookie(response, session_id)
        
        security_auditor.log_security_event(
            event_type="session_created",
            description=f"Nouvelle session créée pour l'utilisateur {user_id}",
            severity="INFO",
            details={"session_id": session_id}
        )
        
        return session_id

    def get_session(
        self,
        request: Request
    ) -> Optional[Dict[str, Any]]:
        """Récupère une session.
        
        Args:
            request: Requête HTTP
            
        Returns:
            Données de session ou None si invalide
        """
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None
            
        try:
            session_data = self._redis.get(f"{self._prefix}{session_id}")
            if not session_data:
                return None
                
            data = self._serializer.loads(
                session_data,
                max_age=security_settings.SESSION_MAX_AGE
            )
            
            # Met à jour le timestamp de dernière activité
            data["last_activity"] = datetime.utcnow().isoformat()
            self._redis.setex(
                f"{self._prefix}{session_id}",
                security_settings.SESSION_MAX_AGE,
                self._serializer.dumps(data)
            )
            
            return data
            
        except Exception as e:
            security_auditor.log_security_event(
                event_type="session_error",
                description="Erreur lors de la récupération de session",
                severity="WARNING",
                details={"error": str(e)}
            )
            return None

    def update_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Met à jour une session.
        
        Args:
            session_id: ID de session
            data: Nouvelles données
            
        Returns:
            True si la mise à jour a réussi
        """
        try:
            session_data = self._redis.get(f"{self._prefix}{session_id}")
            if not session_data:
                return False
                
            current_data = self._serializer.loads(session_data)
            current_data["data"].update(data)
            current_data["last_activity"] = datetime.utcnow().isoformat()
            
            self._redis.setex(
                f"{self._prefix}{session_id}",
                security_settings.SESSION_MAX_AGE,
                self._serializer.dumps(current_data)
            )
            
            return True
            
        except Exception as e:
            security_auditor.log_security_event(
                event_type="session_error",
                description="Erreur lors de la mise à jour de session",
                severity="WARNING",
                details={"error": str(e)}
            )
            return False

    def delete_session(
        self,
        session_id: str,
        response: Optional[Response] = None
    ) -> None:
        """Supprime une session.
        
        Args:
            session_id: ID de session
            response: Réponse HTTP pour supprimer le cookie
        """
        self._redis.delete(f"{self._prefix}{session_id}")
        
        if response:
            response.delete_cookie(
                "session_id",
                secure=security_settings.SESSION_SECURE,
                httponly=security_settings.SESSION_HTTPONLY,
                samesite=security_settings.SESSION_SAMESITE
            )
            
        security_auditor.log_security_event(
            event_type="session_deleted",
            description="Session supprimée",
            severity="INFO",
            details={"session_id": session_id}
        )

    def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées.
        
        Returns:
            Nombre de sessions supprimées
        """
        count = 0
        for key in self._redis.scan_iter(f"{self._prefix}*"):
            try:
                session_data = self._redis.get(key)
                if not session_data:
                    continue
                    
                data = self._serializer.loads(session_data)
                expires_at = datetime.fromisoformat(data["expires_at"])
                
                if datetime.utcnow() > expires_at:
                    self._redis.delete(key)
                    count += 1
                    
            except Exception:
                # Supprime les sessions invalides
                self._redis.delete(key)
                count += 1
                
        if count > 0:
            security_auditor.log_security_event(
                event_type="sessions_cleaned",
                description=f"{count} sessions expirées supprimées",
                severity="INFO"
            )
            
        return count

    def _set_session_cookie(
        self,
        response: Response,
        session_id: str
    ) -> None:
        """Définit le cookie de session.
        
        Args:
            response: Réponse HTTP
            session_id: ID de session
        """
        response.set_cookie(
            "session_id",
            session_id,
            max_age=security_settings.SESSION_MAX_AGE,
            secure=security_settings.SESSION_SECURE,
            httponly=security_settings.SESSION_HTTPONLY,
            samesite=security_settings.SESSION_SAMESITE
        )

# Instance globale du gestionnaire de session
session_manager = SessionManager() 