"""Module contenant les repositories de patterns."""
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Pattern

class PatternsRepository(ABC):
    """Classe abstraite pour les repositories de patterns."""
    
    @abstractmethod
    def get_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les patterns d'analyse."""
        pass

class TypeScriptPatternsRepository(PatternsRepository):
    """Repository des patterns TypeScript."""
    
    def get_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les patterns de sécurité TypeScript."""
        return {
            'eval': {
                'pattern': re.compile(r'eval\s*\('),
                'severity': 'high',
                'description': 'Utilisation dangereuse de eval()',
                'cwe': 'CWE-95'
            },
            'exec': {
                'pattern': re.compile(r'exec\s*\('),
                'severity': 'high',
                'description': 'Exécution de commandes système non sécurisée',
                'cwe': 'CWE-78'
            },
            'sensitive_files': {
                'pattern': re.compile(r'readFileSync\s*\([\'"](?:/etc/)?(?:passwd|shadow|credentials)[\'"]'),
                'severity': 'high',
                'description': 'Accès à des fichiers système sensibles',
                'cwe': 'CWE-732'
            }
        }
