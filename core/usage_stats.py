from datetime import datetime
import json
from pathlib import Path
import os
from .logger import logger

class UsageStats:
    def __init__(self):
        """Initialise le suivi des statistiques."""
        self.stats_file = Path('data/usage_stats.json')
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self.enabled = os.getenv('ENABLE_USAGE_STATS', 'true').lower() == 'true'
        
        # Charger les stats existantes
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Charge les statistiques depuis le fichier."""
        if not self.stats_file.exists():
            return {
                'total_analyses': 0,
                'analyses_by_service': {},
                'analyses_by_date': {},
                'errors': 0
            }
        
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des stats: {e}")
            return {}
    
    def _save_stats(self):
        """Sauvegarde les statistiques."""
        if not self.enabled:
            return
            
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des stats: {e}")
    
    def record_analysis(self, service: str):
        """Enregistre une nouvelle analyse."""
        if not self.enabled:
            return
            
        # Incrémenter le total
        self.stats['total_analyses'] += 1
        
        # Stats par service
        self.stats['analyses_by_service'][service] = \
            self.stats['analyses_by_service'].get(service, 0) + 1
        
        # Stats par date
        today = datetime.now().strftime('%Y-%m-%d')
        self.stats['analyses_by_date'][today] = \
            self.stats['analyses_by_date'].get(today, 0) + 1
        
        self._save_stats()
    
    def record_error(self):
        """Enregistre une erreur."""
        if not self.enabled:
            return
            
        self.stats['errors'] += 1
        self._save_stats() 