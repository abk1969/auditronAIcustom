"""Optimiseur de requêtes IA."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import hashlib
from datetime import datetime, timedelta

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry
from ..cache.smart_cache import SmartCache
from .service_factory import AIServiceFactory

@dataclass
class QueryStats:
    """Statistiques d'une requête."""
    tokens: int
    duration: float
    cost: float
    cache_hit: bool

class QueryOptimizer:
    """Optimiseur de requêtes IA."""
    
    def __init__(self, cache: SmartCache):
        """
        Initialise l'optimiseur.
        
        Args:
            cache: Instance du cache intelligent
        """
        self.cache = cache
        self.ai_service = AIServiceFactory.get_service()
        self.query_history: List[Dict[str, Any]] = []
    
    def _compute_query_hash(self, prompt: str, **kwargs) -> str:
        """Calcule le hash d'une requête."""
        query_data = {
            'prompt': prompt,
            **kwargs
        }
        return hashlib.sha256(
            json.dumps(query_data, sort_keys=True).encode()
        ).hexdigest()
    
    @telemetry.trace_method("optimize_query")
    async def optimize_query(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Optimise et exécute une requête.
        
        Args:
            prompt: Prompt de la requête
            max_tokens: Nombre maximum de tokens
            temperature: Température pour la génération
            **kwargs: Arguments additionnels
            
        Returns:
            Dict contenant la réponse et les statistiques
        """
        try:
            start_time = datetime.now()
            
            # Calculer le hash de la requête
            query_hash = self._compute_query_hash(prompt, **kwargs)
            
            # Vérifier le cache
            cached_result = self.cache.get(query_hash)
            if cached_result:
                return {
                    **cached_result,
                    'stats': QueryStats(
                        tokens=cached_result.get('tokens', 0),
                        duration=0.0,
                        cost=0.0,
                        cache_hit=True
                    ).__dict__
                }
            
            # Optimiser les paramètres
            optimized_params = self._optimize_parameters(prompt, **kwargs)
            
            # Exécuter la requête
            response = await self.ai_service.generate(
                prompt,
                max_tokens=max_tokens or optimized_params.get('max_tokens'),
                temperature=temperature or optimized_params.get('temperature'),
                **kwargs
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Calculer les statistiques
            stats = QueryStats(
                tokens=len(prompt.split()) + len(response.split()),
                duration=duration,
                cost=self._estimate_cost(prompt, response),
                cache_hit=False
            )
            
            result = {
                'response': response,
                'stats': stats.__dict__
            }
            
            # Mettre en cache
            self.cache.set(query_hash, result)
            
            # Mettre à jour l'historique
            self.query_history.append({
                'timestamp': datetime.now().isoformat(),
                'query_hash': query_hash,
                'stats': stats.__dict__
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation de la requête: {e}")
            raise
    
    def _optimize_parameters(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Optimise les paramètres de la requête."""
        # Analyse du prompt pour optimiser les paramètres
        word_count = len(prompt.split())
        
        params = {
            'max_tokens': min(4000, word_count * 2),  # Estimation de la longueur de réponse
            'temperature': 0.7  # Valeur par défaut
        }
        
        # Ajuster la température selon le contexte
        if 'analyze' in prompt.lower() or 'evaluate' in prompt.lower():
            params['temperature'] = 0.3  # Plus déterministe pour l'analyse
        elif 'creative' in prompt.lower() or 'generate' in prompt.lower():
            params['temperature'] = 0.9  # Plus créatif
            
        return params
    
    def _estimate_cost(self, prompt: str, response: str) -> float:
        """Estime le coût de la requête."""
        # Estimation basique basée sur le nombre de tokens
        prompt_tokens = len(prompt.split())
        response_tokens = len(response.split())
        
        # Coût approximatif par token (à ajuster selon le modèle)
        cost_per_token = 0.00002
        
        return (prompt_tokens + response_tokens) * cost_per_token
    
    @telemetry.trace_method("analyze_performance")
    def analyze_performance(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Analyse les performances des requêtes.
        
        Args:
            time_window: Fenêtre de temps pour l'analyse
            
        Returns:
            Dict contenant les métriques de performance
        """
        try:
            # Filtrer l'historique par fenêtre de temps
            cutoff = datetime.now() - time_window
            recent_queries = [
                q for q in self.query_history
                if datetime.fromisoformat(q['timestamp']) > cutoff
            ]
            
            if not recent_queries:
                return {
                    'query_count': 0,
                    'cache_hit_rate': 0.0,
                    'avg_duration': 0.0,
                    'total_cost': 0.0
                }
            
            # Calculer les métriques
            cache_hits = sum(1 for q in recent_queries if q['stats']['cache_hit'])
            total_duration = sum(q['stats']['duration'] for q in recent_queries)
            total_cost = sum(q['stats']['cost'] for q in recent_queries)
            
            return {
                'query_count': len(recent_queries),
                'cache_hit_rate': cache_hits / len(recent_queries),
                'avg_duration': total_duration / len(recent_queries),
                'total_cost': total_cost
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des performances: {e}")
            return {} 