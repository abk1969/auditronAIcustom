"""
AuditronAI.core
--------------
Modules principaux pour l'analyse de code et la sécurité.
"""

__all__ = [
    'SecurityAnalyzer',
    'setup_logger',
    'AnalysisHistory'
]

from .logger import setup_logger
from .history import AnalysisHistory

def SecurityAnalyzer(*args, **kwargs):
    """Classe d'analyse de sécurité."""
    from .security_analyzer import SecurityAnalyzer as _SecurityAnalyzer
    return _SecurityAnalyzer(*args, **kwargs)
