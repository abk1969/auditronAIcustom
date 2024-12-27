"""Exemple de plugin d'analyse."""
from typing import Dict, Any
from AuditronAI.core.plugins.base import PluginInterface, PluginMetadata, PluginType

class Plugin(PluginInterface):
    """Plugin d'exemple pour l'analyse de complexité."""
    
    def __init__(self):
        self._config = {}
        
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="complexity_analyzer",
            version="1.0.0",
            description="Analyse la complexité du code",
            author="AuditronAI Team",
            plugin_type=PluginType.ANALYZER,
            dependencies=["radon>=5.1.0"]
        )
        
    def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config
        
    def execute(self, code: str) -> Dict[str, Any]:
        """Analyse la complexité du code."""
        import radon.complexity as cc
        
        try:
            results = cc.cc_visit(code)
            return {
                'complexity_score': sum(result.complexity for result in results),
                'details': [
                    {
                        'name': result.name,
                        'complexity': result.complexity,
                        'line': result.lineno
                    }
                    for result in results
                ]
            }
        except Exception as e:
            return {'error': str(e)}
            
    def cleanup(self) -> None:
        self._config = {} 