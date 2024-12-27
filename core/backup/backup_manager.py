"""Gestionnaire de sauvegardes."""
from typing import Dict, Any, List, Optional
from pathlib import Path
import shutil
import tarfile
import json
from datetime import datetime
import asyncio
import aiofiles
import os

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry
from ..compression.data_compressor import DataCompressor

class BackupManager:
    """Gestionnaire de sauvegardes."""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Initialise le gestionnaire de sauvegardes.
        
        Args:
            backup_dir: Répertoire des sauvegardes
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.compressor = DataCompressor()
        
    @telemetry.trace_method("create_backup")
    async def create_backup(self, data_dir: str, metadata: Dict[str, Any] = None) -> str:
        """
        Crée une sauvegarde.
        
        Args:
            data_dir: Répertoire à sauvegarder
            metadata: Métadonnées de la sauvegarde
            
        Returns:
            str: Identifiant de la sauvegarde
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"backup_{timestamp}"
            
            # Créer le répertoire de sauvegarde
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir()
            
            # Sauvegarder les métadonnées
            if metadata:
                metadata_file = backup_path / "metadata.json"
                async with aiofiles.open(metadata_file, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2))
            
            # Créer l'archive
            archive_path = backup_path / f"{backup_id}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(data_dir, arcname=os.path.basename(data_dir))
            
            # Compresser l'archive
            async with aiofiles.open(archive_path, 'rb') as f:
                data = await f.read()
                compressed = self.compressor.compress(data)
            
            compressed_path = backup_path / f"{backup_id}.compressed"
            async with aiofiles.open(compressed_path, 'wb') as f:
                await f.write(compressed['data'].encode())
            
            logger.info(f"Sauvegarde créée: {backup_id}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            raise
    
    @telemetry.trace_method("restore_backup")
    async def restore_backup(self, backup_id: str, restore_dir: str) -> bool:
        """
        Restaure une sauvegarde.
        
        Args:
            backup_id: Identifiant de la sauvegarde
            restore_dir: Répertoire de restauration
        """
        try:
            backup_path = self.backup_dir / backup_id
            if not backup_path.exists():
                raise ValueError(f"Sauvegarde non trouvée: {backup_id}")
            
            # Restaurer les données
            compressed_path = backup_path / f"{backup_id}.compressed"
            async with aiofiles.open(compressed_path, 'rb') as f:
                compressed_data = await f.read()
                
            decompressed = self.compressor.decompress({
                'data': compressed_data.decode(),
                'algorithm': 'zlib'
            })
            
            archive_path = backup_path / f"{backup_id}.tar.gz"
            async with aiofiles.open(archive_path, 'wb') as f:
                await f.write(decompressed)
            
            # Extraire l'archive
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=restore_dir)
            
            logger.info(f"Sauvegarde restaurée: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """Liste les sauvegardes disponibles."""
        try:
            backups = []
            
            for backup_dir in self.backup_dir.iterdir():
                if not backup_dir.is_dir():
                    continue
                    
                metadata_file = backup_dir / "metadata.json"
                metadata = {}
                
                if metadata_file.exists():
                    async with aiofiles.open(metadata_file, 'r') as f:
                        content = await f.read()
                        metadata = json.loads(content)
                
                stats = backup_dir.stat()
                backups.append({
                    'id': backup_dir.name,
                    'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    'size': sum(f.stat().st_size for f in backup_dir.glob('**/*')),
                    'metadata': metadata
                })
            
            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Erreur lors de la liste des sauvegardes: {e}")
            return [] 