"""Gestionnaire de rate limiting pour AuditronAI."""

import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import DefaultDict, Dict, List, Optional, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .security_config import security_settings
from .security_auditor import security_auditor

@dataclass
class RateLimitRule:
    """Règle de rate limiting."""
    
    requests: int  # Nombre de requêtes autorisées
    window: int   # Fenêtre de temps en secondes
    block_time: Optional[int] = None  # Temps de blocage en secondes

class RateLimiter:
    """Gestionnaire de rate limiting."""

    def __init__(self) -> None:
        """Initialise le rate limiter."""
        # Stockage des tentatives par IP
        self._attempts: DefaultDict[str, List[float]] = defaultdict(list)
        
        # Stockage des IP bloquées avec leur temps de déblocage
        self._blocked: Dict[str, float] = {}
        
        # Règles par défaut
        self.default_rules = {
            "global": RateLimitRule(
                requests=1000,
                window=3600,  # 1 heure
                block_time=3600  # 1 heure
            ),
            "auth": RateLimitRule(
                requests=5,
                window=300,  # 5 minutes
                block_time=1800  # 30 minutes
            ),
            "api": RateLimitRule(
                requests=100,
                window=60,  # 1 minute
                block_time=300  # 5 minutes
            )
        }

    def is_blocked(self, ip: str) -> bool:
        """Vérifie si une IP est bloquée.
        
        Args:
            ip: Adresse IP à vérifier
            
        Returns:
            True si l'IP est bloquée
        """
        if ip in self._blocked:
            if time.time() >= self._blocked[ip]:
                del self._blocked[ip]
                return False
            return True
        return False

    def block_ip(self, ip: str, duration: int) -> None:
        """Bloque une IP pour une durée donnée.
        
        Args:
            ip: Adresse IP à bloquer
            duration: Durée du blocage en secondes
        """
        self._blocked[ip] = time.time() + duration
        
        security_auditor.log_security_event(
            event_type="ip_blocked",
            description=f"IP {ip} bloquée pour {duration} secondes",
            severity="WARNING",
            details={"ip": ip, "duration": duration}
        )

    def record_request(self, ip: str) -> None:
        """Enregistre une requête pour une IP.
        
        Args:
            ip: Adresse IP
        """
        now = time.time()
        self._attempts[ip].append(now)
        
        # Nettoyage des anciennes tentatives
        self._cleanup_old_attempts(ip)

    def _cleanup_old_attempts(self, ip: str) -> None:
        """Nettoie les anciennes tentatives pour une IP.
        
        Args:
            ip: Adresse IP à nettoyer
        """
        now = time.time()
        max_window = max(rule.window for rule in self.default_rules.values())
        
        self._attempts[ip] = [
            t for t in self._attempts[ip]
            if now - t <= max_window
        ]
        
        if not self._attempts[ip]:
            del self._attempts[ip]

    def check_rate_limit(
        self,
        ip: str,
        rule_type: str = "global"
    ) -> Tuple[bool, Optional[int]]:
        """Vérifie si une IP dépasse la limite.
        
        Args:
            ip: Adresse IP à vérifier
            rule_type: Type de règle à appliquer
            
        Returns:
            Tuple (allowed, retry_after)
            - allowed: Si la requête est autorisée
            - retry_after: Temps d'attente en secondes si bloqué
        """
        if self.is_blocked(ip):
            block_remaining = int(self._blocked[ip] - time.time())
            return False, block_remaining

        rule = self.default_rules[rule_type]
        now = time.time()
        
        # Compte les requêtes dans la fenêtre
        recent_attempts = len([
            t for t in self._attempts[ip]
            if now - t <= rule.window
        ])
        
        if recent_attempts >= rule.requests:
            if rule.block_time:
                self.block_ip(ip, rule.block_time)
                return False, rule.block_time
                
            oldest_allowed = now - rule.window
            next_allowed = min(
                t for t in self._attempts[ip]
                if t > oldest_allowed
            ) + rule.window
            
            return False, int(next_allowed - now)
            
        return True, None

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialise le middleware."""
        super().__init__(*args, **kwargs)
        self.limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        """Traite la requête en appliquant le rate limiting.
        
        Args:
            request: La requête entrante
            call_next: La fonction à appeler ensuite
            
        Returns:
            La réponse
        """
        ip = request.client.host
        
        # Détermine le type de règle
        if request.url.path.startswith("/auth"):
            rule_type = "auth"
        elif request.url.path.startswith("/api"):
            rule_type = "api"
        else:
            rule_type = "global"
            
        allowed, retry_after = self.limiter.check_rate_limit(ip, rule_type)
        
        if not allowed:
            security_auditor.log_security_event(
                event_type="rate_limit_exceeded",
                description=f"Rate limit dépassé pour {ip}",
                severity="WARNING",
                details={
                    "ip": ip,
                    "rule_type": rule_type,
                    "retry_after": retry_after
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Trop de requêtes",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
            
        self.limiter.record_request(ip)
        return await call_next(request)

# Instance globale du rate limiter
rate_limiter = RateLimiter() 