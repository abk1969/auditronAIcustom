"""Module de gestion de l'historique des analyses."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json

@dataclass
class AnalysisRecord:
    """Représente une entrée dans l'historique des analyses."""
    timestamp: datetime
    filename: str
    score: float
    issues_count: int
    complexity: float
    details: Dict

class AnalysisHistory:
    """Gère l'historique des analyses de sécurité."""
    
    def __init__(self, history_file: Optional[Path] = None):
        """Initialise l'historique.
        
        Args:
            history_file: Chemin vers le fichier d'historique
        """
        self.history_file = history_file or Path.home() / '.auditronai' / 'history.json'
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[AnalysisRecord] = []
        self._load_history()

    def add_record(self, filename: str, score: float, issues_count: int, 
                  complexity: float, details: Dict):
        """Ajoute une nouvelle entrée dans l'historique.
        
        Args:
            filename: Nom du fichier analysé
            score: Score de sécurité
            issues_count: Nombre de problèmes détectés
            complexity: Score de complexité
            details: Détails supplémentaires de l'analyse
        """
        record = AnalysisRecord(
            timestamp=datetime.now(),
            filename=filename,
            score=score,
            issues_count=issues_count,
            complexity=complexity,
            details=details
        )
        self.records.append(record)
        self._save_history()

    def get_records(self, limit: Optional[int] = None) -> List[AnalysisRecord]:
        """Récupère les entrées de l'historique.
        
        Args:
            limit: Nombre maximum d'entrées à retourner
            
        Returns:
            Liste des entrées d'historique
        """
        records = sorted(
            self.records,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return records[:limit] if limit else records

    def clear_history(self):
        """Efface tout l'historique."""
        self.records.clear()
        self._save_history()

    def _load_history(self):
        """Charge l'historique depuis le fichier."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.records = [
                        AnalysisRecord(
                            timestamp=datetime.fromisoformat(r['timestamp']),
                            filename=r['filename'],
                            score=r['score'],
                            issues_count=r['issues_count'],
                            complexity=r['complexity'],
                            details=r['details']
                        )
                        for r in data
                    ]
            except Exception as e:
                print(f"Erreur lors du chargement de l'historique: {e}")
                self.records = []

    def _save_history(self):
        """Sauvegarde l'historique dans le fichier."""
        try:
            with open(self.history_file, 'w') as f:
                records_data = []
                for r in self.records:
                    record_dict = {
                        'timestamp': r.timestamp.isoformat(),
                        'filename': r.filename,
                        'score': r.score,
                        'issues_count': r.issues_count,
                        'complexity': r.complexity,
                    }
                    if hasattr(r.details, 'to_dict'):
                        record_dict['details'] = r.details.to_dict()
                    else:
                        record_dict['details'] = r.details
                    records_data.append(record_dict)
                
                json.dump(records_data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'historique: {e}")
