from openai import OpenAI
import os
from dotenv import load_dotenv

class OpenAIClient:
    def __init__(self):
        load_dotenv()
        
        # Vérification des variables d'environnement requises
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("La variable d'environnement OPENAI_API_KEY est requise")
        
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")

    def generate_completion(self, prompt: str, system_message: str = None, **kwargs):
        try:
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
        except Exception as e:
            print(f"Modèle utilisé : {self.model}")
            raise Exception(f"Erreur lors de la génération : {str(e)}") 