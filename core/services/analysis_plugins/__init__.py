"""Module d'initialisation des plugins d'analyse."""
from typing import Dict, Any
from .base import AnalysisPlugin
from .typescript_plugin import TypeScriptAnalysisPlugin
from .sql_plugin import SQLAnalysisPlugin
from .security_plugin import SecurityPlugin
from .metrics_plugin import MetricsPlugin
from ..plugin_registry import PluginRegistry

__all__ = ['AnalysisPlugin', 'TypeScriptAnalysisPlugin', 'SQLAnalysisPlugin', 'SecurityPlugin', 'MetricsPlugin']

# Register plugins
PluginRegistry.register('typescript', TypeScriptAnalysisPlugin)
PluginRegistry.register('sql', SQLAnalysisPlugin)
PluginRegistry.register('security', SecurityPlugin)
PluginRegistry.register('metrics', MetricsPlugin)
