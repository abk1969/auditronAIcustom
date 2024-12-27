"""Module de chiffrement des données."""
from cryptography.fernet import Fernet
from typing import Any, Optional
import base64
import os
import json
from pathlib import Path

from ..logger import logger
from ..telemetry.opentelemetry_config import telemetry

class EncryptionManager:
    """Gestionnaire de chiffrement."""
    
    def __init__(self):
        """Initialise le gestionnaire de chiffrement."""
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_generate_key(self) -> bytes:
        """Charge ou génère une clé de chiffrement."""
        key_file = Path("config/encryption.key")
        
        try:
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            
            # Générer une nouvelle clé
            key = Fernet.generate_key()
            
            # Sauvegarder la clé
            key_file.parent.mkdir(exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            return key
            
        except Exception as e:
            logger.error(f"Erreur avec la clé de chiffrement: {e}")
            return Fernet.generate_key()
    
    @telemetry.trace_method("encrypt_data")
    def encrypt(self, data: Any) -> str:
        """Chiffre des données."""
        try:
            # Convertir en JSON et encoder en bytes
            json_data = json.dumps(data)
            bytes_data = json_data.encode()
            
            # Chiffrer
            encrypted = self.fernet.encrypt(bytes_data)
            
            # Encoder en base64 pour le stockage
            return base64.b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error(f"Erreur lors du chiffrement: {e}")
            raise
    
    @telemetry.trace_method("decrypt_data")
    def decrypt(self, encrypted_data: str) -> Any:
        """Déchiffre des données."""
        try:
            # Décoder le base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Déchiffrer
            decrypted = self.fernet.decrypt(encrypted_bytes)
            
            # Convertir en objet Python
            return json.loads(decrypted.decode())
            
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement: {e}")
            raise 