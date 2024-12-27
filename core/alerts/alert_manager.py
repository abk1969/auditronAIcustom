"""Gestionnaire d'alertes pour AuditronAI."""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import smtplib
from email.mime.text import MIMEText
import json
import os

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

@dataclass
class AlertRule:
    """Règle d'alerte."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    message_template: str
    severity: str
    cooldown: int  # Période minimale entre deux alertes en secondes
    channels: List[str]

class AlertManager:
    """Gestionnaire d'alertes."""
    
    def __init__(self):
        """Initialise le gestionnaire d'alertes."""
        self.rules: Dict[str, AlertRule] = {}
        self.last_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Charger la configuration
        self._load_config()
        
    def _load_config(self):
        """Charge la configuration des alertes."""
        try:
            # Règles par défaut
            self.rules = {
                'high_error_rate': AlertRule(
                    name='Taux d\'erreur élevé',
                    condition=lambda metrics: metrics.get('error_rate', 0) > 0.1,
                    message_template='Taux d\'erreur de {error_rate:.1%}',
                    severity='high',
                    cooldown=300,  # 5 minutes
                    channels=['email', 'slack']
                ),
                'high_memory_usage': AlertRule(
                    name='Utilisation mémoire élevée',
                    condition=lambda metrics: metrics.get('memory_usage_mb', 0) > 1000,
                    message_template='Utilisation mémoire: {memory_usage_mb}MB',
                    severity='medium',
                    cooldown=600,  # 10 minutes
                    channels=['slack']
                ),
                'api_latency': AlertRule(
                    name='Latence API élevée',
                    condition=lambda metrics: metrics.get('api_latency_ms', 0) > 1000,
                    message_template='Latence API: {api_latency_ms}ms',
                    severity='high',
                    cooldown=300,
                    channels=['email', 'slack']
                )
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration des alertes: {e}")
    
    @telemetry.trace_method("check_alerts")
    async def check_alerts(self, metrics: Dict[str, Any]):
        """
        Vérifie les conditions d'alerte.
        
        Args:
            metrics: Métriques à vérifier
        """
        for rule_id, rule in self.rules.items():
            try:
                # Vérifier le cooldown
                if rule_id in self.last_alerts:
                    elapsed = datetime.now() - self.last_alerts[rule_id]
                    if elapsed.total_seconds() < rule.cooldown:
                        continue
                
                # Vérifier la condition
                if rule.condition(metrics):
                    message = rule.message_template.format(**metrics)
                    await self._send_alert(rule, message, metrics)
                    self.last_alerts[rule_id] = datetime.now()
                    
            except Exception as e:
                logger.error(f"Erreur lors de la vérification de l'alerte {rule_id}: {e}")
    
    async def _send_alert(self, rule: AlertRule, message: str, metrics: Dict[str, Any]):
        """Envoie une alerte sur les canaux configurés."""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'rule': rule.name,
            'severity': rule.severity,
            'message': message,
            'metrics': metrics
        }
        
        self.alert_history.append(alert_data)
        
        for channel in rule.channels:
            try:
                if channel == 'email':
                    await self._send_email_alert(rule, message)
                elif channel == 'slack':
                    await self._send_slack_alert(rule, message)
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'alerte via {channel}: {e}")
    
    async def _send_email_alert(self, rule: AlertRule, message: str):
        """Envoie une alerte par email."""
        try:
            smtp_host = os.getenv('SMTP_HOST', 'localhost')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASS')
            
            msg = MIMEText(message)
            msg['Subject'] = f"[{rule.severity.upper()}] {rule.name}"
            msg['From'] = os.getenv('ALERT_FROM_EMAIL', 'alerts@auditronai.com')
            msg['To'] = os.getenv('ALERT_TO_EMAIL', 'admin@auditronai.com')
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            raise
    
    async def _send_slack_alert(self, rule: AlertRule, message: str):
        """Envoie une alerte sur Slack."""
        try:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                logger.error("URL Webhook Slack non configurée")
                return
                
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    'text': f"*[{rule.severity.upper()}] {rule.name}*\n{message}"
                }
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Erreur Slack: {await response.text()}")
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi sur Slack: {e}")
            raise 