"""
AuditronAI - Analyseur de code Python avec IA
"""

__version__ = "0.1.0"

from .core import SecurityAnalyzer, setup_logger, AnalysisHistory

__all__ = [
    'SecurityAnalyzer',
    'setup_logger',
    'AnalysisHistory',
    '__version__'
]