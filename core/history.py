import json
from pathlib import Path
from datetime import datetime
import os
from typing import List, Dict, Any
from .logger import logger

class AnalysisHistory:
    def __init__(self):
        """Initialise le gestionnaire d'historique."""
        self.history_file = Path(os.getenv('HISTORY_FILE', 'data/history.json'))
        self.max_entries = int(os.getenv('HISTORY_MAX_ENTRIES', 1000))
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger l'historique existant
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Charge l'historique depuis le fichier."""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'historique: {e}")
            return []
    
    def _save_history(self):
        """Sauvegarde l'historique dans le fichier."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {e}")
    
    def add_entry(self, entry: Dict[str, Any]):
        """Ajoute une nouvelle entrée à l'historique."""
        # Ajouter timestamp
        entry['timestamp'] = datetime.now().isoformat()
        
        # Ajouter l'entrée
        self.history.append(entry)
        
        # Limiter la taille
        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries:]
        
        # Sauvegarder
        self._save_history()
        logger.info(f"Nouvelle analyse ajoutée à l'historique: {entry['file']}")
    
    def get_entries(self, limit: int = None) -> List[Dict[str, Any]]:
        """Récupère les entrées de l'historique."""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """Efface tout l'historique."""
        self.history = []
        self._save_history()
        logger.warning("Historique effacé") 