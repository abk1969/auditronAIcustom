"""Client Google Gemini pour AuditronAI."""
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .ai_factory import TimeoutManager, limit_memory, TimeoutError
from .logger import logger

class GeminiClient:
    """Client pour l'API Google Gemini."""
    
    VALID_MODELS = [
        'gemini-2.0-flash-exp',  # Version rapide
        'gemini-pro',            # Version standard
        'gemini-pro-vision'      # Version avec support d'images
    ]
    
    def __init__(self):
        """Initialise le client Gemini."""
        load_dotenv()
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("La variable d'environnement GOOGLE_API_KEY est requise")
            
        genai.configure(api_key=api_key)
        
        model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash-exp")
        if model not in self.VALID_MODELS:
            logger.warning(f"Modèle {model} non reconnu, utilisation de gemini-2.0-flash-exp par défaut")
            model = "gemini-2.0-flash-exp"
        self.model = model
        
    def generate_completion(self, prompt: str, system_message: str = None, **kwargs):
        """
        Génère une complétion avec Gemini.
        
        Args:
            prompt: Le prompt à compléter
            system_message: Message système optionnel (ajouté au prompt)
            **kwargs: Arguments additionnels pour l'API
            
        Returns:
            str: La réponse générée
        """
        try:
            # Limiter la mémoire
            limit_memory(1000)
            
            with TimeoutManager(30):  # Timeout de 30 secondes
                model = genai.GenerativeModel(self.model)
                
                # Combiner system message et prompt si nécessaire
                full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
                
                response = model.generate_content(full_prompt)
                return response.text
                
        except TimeoutError:
            logger.error(f"Timeout lors de la génération avec {self.model}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec {self.model}: {str(e)}")
            raise