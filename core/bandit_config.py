"""Configuration de Bandit pour AuditronAI."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ScanLevel(str, Enum):
    """Niveaux de scan disponibles."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

@dataclass
class BanditProfile:
    """Profile de configuration Bandit."""
    name: str
    tests: List[str]
    confidence_threshold: float
    severity_threshold: str

    @classmethod
    def default(cls) -> 'BanditProfile':
        """Retourne le profil par défaut."""
        return cls(
            name='default',
            tests=['B102', 'B103', 'B104', 'B105', 'B106', 'B107'],
            confidence_threshold=0.8,
            severity_threshold=ScanLevel.HIGH
        )

def get_bandit_config(
    scan_level: str,
    min_confidence: float,
    max_issues: int,
    profile: Optional[str] = None,
    tests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retourne la configuration Bandit optimisée.
    
    Args:
        scan_level: Niveau de scan ('low', 'medium', 'high')
        min_confidence: Niveau de confiance minimum (0.0-1.0)
        max_issues: Nombre maximum de problèmes à rapporter
        profile: Profil Bandit à utiliser (default par défaut)
        tests: Liste des tests Bandit à exécuter (optionnel)
    """
    # Validation des paramètres
    try:
        scan_level = ScanLevel(scan_level.lower())
    except ValueError:
        raise ValueError(f"Niveau de scan invalide. Valeurs possibles : {[e.value for e in ScanLevel]}")

    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("Le niveau de confiance doit être entre 0.0 et 1.0")

    if max_issues < 1:
        raise ValueError("Le nombre maximum de problèmes doit être positif")

    # Configuration de base
    config = {
        'plugin_name_pattern': '*.py',
        'exclude_pattern': None,
        'recursive': False,
        'aggregate': 'file',
        'level': scan_level.value.upper(),
        'confidence': int(min_confidence * 10),
        'output_format': 'json',
        'number': max_issues,
        'quiet': True,
        'ignore_nosec': False
    }

    # Ajouter le profil et les tests si spécifiés
    if profile:
        config['profile'] = profile
    if tests:
        config['tests'] = [t.strip() for t in tests if t.strip()]

    return config