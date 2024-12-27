"""Factory pour les services d'IA."""
from typing import Dict, Any, Optional, Type
from abc import ABC, abstractmethod
import os

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

class AIService(ABC):
    """Interface abstraite pour les services d'IA."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Génère une réponse."""
        pass
    
    @abstractmethod
    async def analyze(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyse du code."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Vérifie l'état du service."""
        pass

class OpenAIService(AIService):
    """Service OpenAI."""
    
    def __init__(self):
        """Initialise le service OpenAI."""
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            timeout=30
        )
    
    @telemetry.trace_method("openai_generate")
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4'),
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            raise

class GeminiService(AIService):
    """Service Google Gemini."""
    
    def __init__(self):
        """Initialise le service Gemini."""
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(
            os.getenv('GOOGLE_MODEL', 'gemini-pro')
        )
    
    @telemetry.trace_method("gemini_generate")
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erreur Gemini: {e}")
            raise

class AIServiceFactory:
    """Factory pour les services d'IA."""
    
    _services: Dict[str, Type[AIService]] = {
        'openai': OpenAIService,
        'gemini': GeminiService
    }
    
    @classmethod
    def get_service(cls, name: str = None) -> AIService:
        """
        Retourne une instance du service demandé.
        
        Args:
            name: Nom du service (si None, utilise AI_SERVICE de l'env)
        """
        service_name = name or os.getenv('AI_SERVICE', 'openai')
        
        if service_name not in cls._services:
            raise ValueError(f"Service inconnu: {service_name}")
            
        return cls._services[service_name]()
    
    @classmethod
    def register_service(cls, name: str, service_class: Type[AIService]):
        """Enregistre un nouveau service."""
        cls._services[name] = service_class 