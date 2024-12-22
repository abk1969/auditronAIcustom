"""Client OpenAI pour AuditronAI."""
from openai import OpenAI
import os
from dotenv import load_dotenv
from .ai_factory import TimeoutManager, limit_memory, TimeoutError
from .logger import logger

class OpenAIClient:
    # Liste des modèles valides
    VALID_MODELS = [
        'gpt-4o-mini',           # Version économique
        'gpt-4o',                # Version standard
        'gpt-4o-audio-preview',  # Version avec support audio
        'gpt-4'                  # Fallback model
    ]
    
    def __init__(self):
        """Initialise le client OpenAI."""
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("La variable d'environnement OPENAI_API_KEY est requise")
        
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Vérification et configuration du modèle
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        if model not in self.VALID_MODELS:
            print(f"Warning: Modèle {model} non reconnu, utilisation de gpt-4 par défaut")
            model = "gpt-4"
        self.model = model

    def generate_completion(self, prompt: str, system_message: str = None, **kwargs):
        """
        Génère une complétion avec OpenAI.
        
        Args:
            prompt: Le prompt à compléter
            system_message: Message système optionnel
            **kwargs: Arguments additionnels pour l'API
            
        Returns:
            str: La réponse générée
        """
        try:
            # Limiter la mémoire
            limit_memory(1000)
            
            with TimeoutManager(30):  # Timeout de 30 secondes
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
                
        except TimeoutError:
            logger.error(f"Timeout lors de la génération avec {self.model}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec {self.model}: {str(e)}")
            raise 