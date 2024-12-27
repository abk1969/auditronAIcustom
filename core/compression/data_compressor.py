"""Module de compression des données."""
from typing import Any, Dict, Optional
import zlib
import lz4.frame
import json
import base64
from dataclasses import dataclass

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

@dataclass
class CompressionStats:
    """Statistiques de compression."""
    original_size: int
    compressed_size: int
    ratio: float
    algorithm: str

class DataCompressor:
    """Gestionnaire de compression des données."""
    
    ALGORITHMS = {
        'zlib': {
            'compress': lambda data: zlib.compress(data, level=9),
            'decompress': zlib.decompress
        },
        'lz4': {
            'compress': lz4.frame.compress,
            'decompress': lz4.frame.decompress
        }
    }
    
    def __init__(self, default_algorithm: str = 'zlib'):
        """
        Initialise le compresseur.
        
        Args:
            default_algorithm: Algorithme par défaut
        """
        if default_algorithm not in self.ALGORITHMS:
            raise ValueError(f"Algorithme inconnu: {default_algorithm}")
            
        self.default_algorithm = default_algorithm
    
    @telemetry.trace_method("compress_data")
    def compress(self, data: Any, algorithm: Optional[str] = None) -> Dict[str, Any]:
        """
        Compresse des données.
        
        Args:
            data: Données à compresser
            algorithm: Algorithme à utiliser
            
        Returns:
            Dict contenant les données compressées et les métadonnées
        """
        try:
            # Sérialiser en JSON
            json_data = json.dumps(data).encode()
            original_size = len(json_data)
            
            # Sélectionner l'algorithme
            algo = algorithm or self.default_algorithm
            if algo not in self.ALGORITHMS:
                raise ValueError(f"Algorithme inconnu: {algo}")
            
            # Compresser
            compressed = self.ALGORITHMS[algo]['compress'](json_data)
            compressed_size = len(compressed)
            
            # Encoder en base64 pour le stockage
            encoded = base64.b64encode(compressed).decode()
            
            # Calculer les statistiques
            stats = CompressionStats(
                original_size=original_size,
                compressed_size=compressed_size,
                ratio=compressed_size / original_size,
                algorithm=algo
            )
            
            return {
                'data': encoded,
                'algorithm': algo,
                'stats': stats.__dict__
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la compression: {e}")
            raise
    
    @telemetry.trace_method("decompress_data")
    def decompress(self, compressed_data: Dict[str, Any]) -> Any:
        """
        Décompresse des données.
        
        Args:
            compressed_data: Données compressées avec métadonnées
            
        Returns:
            Données décompressées
        """
        try:
            # Récupérer l'algorithme
            algo = compressed_data['algorithm']
            if algo not in self.ALGORITHMS:
                raise ValueError(f"Algorithme inconnu: {algo}")
            
            # Décoder le base64
            decoded = base64.b64decode(compressed_data['data'])
            
            # Décompresser
            decompressed = self.ALGORITHMS[algo]['decompress'](decoded)
            
            # Désérialiser le JSON
            return json.loads(decompressed.decode())
            
        except Exception as e:
            logger.error(f"Erreur lors de la décompression: {e}")
            raise 