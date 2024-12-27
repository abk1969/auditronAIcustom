"""Système d'audit de sécurité."""
from typing import Dict, Any, List
import asyncio
from datetime import datetime
import json
from pathlib import Path

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry
from .encryption import EncryptionManager

class SecurityAudit:
    """Audit de sécurité automatisé."""
    
    def __init__(self):
        """Initialise l'audit de sécurité."""
        self.encryption = EncryptionManager()
        self.audit_dir = Path("logs/audit")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
    
    @telemetry.trace_method("audit_event")
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Enregistre un événement d'audit."""
        try:
            event = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': event_type,
                'data': data
            }
            
            # Chiffrer les données sensibles
            encrypted_data = self.encryption.encrypt(event)
            
            # Sauvegarder dans un fichier
            file_path = self.audit_dir / f"{datetime.utcnow().date()}.audit"
            async with aiofiles.open(file_path, 'a') as f:
                await f.write(encrypted_data + '\n')
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'audit: {e}")
    
    @telemetry.trace_method("analyze_audit")
    async def analyze_logs(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Analyse les logs d'audit."""
        try:
            events = []
            
            # Parcourir les fichiers d'audit
            for file_path in self.audit_dir.glob("*.audit"):
                file_date = datetime.strptime(file_path.stem, "%Y-%m-%d").date()
                
                if start_date.date() <= file_date <= end_date.date():
                    async with aiofiles.open(file_path, 'r') as f:
                        async for line in f:
                            try:
                                # Déchiffrer l'événement
                                event = self.encryption.decrypt(line.strip())
                                event_time = datetime.fromisoformat(event['timestamp'])
                                
                                if start_date <= event_time <= end_date:
                                    events.append(event)
                                    
                            except Exception as e:
                                logger.error(f"Erreur lors du déchiffrement: {e}")
            
            return events
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des logs: {e}")
            return []
    
    @telemetry.trace_method("security_check")
    async def run_security_check(self) -> Dict[str, Any]:
        """Exécute une vérification de sécurité."""
        try:
            # Vérifier les permissions des fichiers
            file_issues = await self._check_file_permissions()
            
            # Vérifier les tentatives d'accès suspectes
            access_issues = await self._check_suspicious_access()
            
            # Vérifier les configurations sensibles
            config_issues = await self._check_sensitive_configs()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'file_issues': file_issues,
                'access_issues': access_issues,
                'config_issues': config_issues,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de sécurité: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'status': 'failed'
            }
    
    async def _check_file_permissions(self) -> List[Dict[str, Any]]:
        """Vérifie les permissions des fichiers sensibles."""
        issues = []
        sensitive_paths = [
            Path("config"),
            Path("logs"),
            self.audit_dir
        ]
        
        for path in sensitive_paths:
            if path.exists():
                try:
                    # Vérifier les permissions
                    stats = path.stat()
                    if stats.st_mode & 0o777 != 0o700:
                        issues.append({
                            'path': str(path),
                            'current_mode': oct(stats.st_mode & 0o777),
                            'recommended_mode': '0o700',
                            'severity': 'high'
                        })
                except Exception as e:
                    logger.error(f"Erreur lors de la vérification des permissions: {e}")
        
        return issues
    
    async def _check_suspicious_access(self) -> List[Dict[str, Any]]:
        """Vérifie les tentatives d'accès suspectes."""
        # Implémenter la logique de détection d'accès suspects
        return []
    
    async def _check_sensitive_configs(self) -> List[Dict[str, Any]]:
        """Vérifie les configurations sensibles."""
        # Implémenter la vérification des configurations
        return [] 