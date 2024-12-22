"""Module de gestion des datasets personnalisés."""
from typing import List, Dict, Any
import json
import os
from pathlib import Path

class CustomDataset:
    def __init__(self, dataset_name: str):
        """Initialise le dataset."""
        self.dataset_name = dataset_name
        # Import ici pour éviter les imports circulaires
        from .ai_factory import get_ai_client
        from .prompt_manager import PromptManager
        
        self.ai_client = get_ai_client()
        self.prompt_manager = PromptManager()
        self.dataset_path = Path("datasets") / f"{dataset_name}.json"
        
        # Créer le dossier datasets s'il n'existe pas
        os.makedirs("datasets", exist_ok=True)
        
        # Charger ou créer le dataset
        self.data = self._load_dataset()
    
    def _load_dataset(self) -> List[Dict[str, Any]]:
        if self.dataset_path.exists():
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_dataset(self):
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def generate_completion(self, prompt_name: str, input_data: Dict[str, Any]) -> str:
        # Obtenir le prompt configuré
        prompt_config = self.prompt_manager.get_prompt(prompt_name, **input_data)
        
        # Générer la complétion
        response = self.ai_client.generate_completion(
            prompt_config['user'],
            system_message=prompt_config.get('system'),
            temperature=prompt_config.get('temperature', 0.7),
            max_tokens=prompt_config.get('max_tokens', 1000)
        )
        
        # Sauvegarder les résultats
        result = {
            "input": input_data,
            "prompt_name": prompt_name,
            "response": response
        }
        self.data.append(result)
        self.save_dataset()
        
        return response

    def get_results(self) -> List[Dict[str, Any]]:
        return self.data
