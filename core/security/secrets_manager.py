"""Gestionnaire de secrets sécurisé pour AuditronAI."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from dotenv import load_dotenv
from loguru import logger

class SecretsManager:
    """Gestionnaire de secrets avec chiffrement."""

    def __init__(self, secrets_file: str = ".secrets.enc"):
        """Initialise le gestionnaire de secrets.
        
        Args:
            secrets_file: Chemin vers le fichier de secrets chiffré
        """
        load_dotenv()
        self._secrets_file = Path(secrets_file)
        self._key = self._generate_key()
        self._fernet = Fernet(self._key)
        self._secrets: Dict[str, Any] = {}
        self._load_secrets()

    def _generate_key(self) -> bytes:
        """Génère une clé de chiffrement à partir d'une phrase secrète."""
        secret = os.getenv("SECRET_KEY")
        if not secret:
            raise ValueError("SECRET_KEY non d��finie dans les variables d'environnement")

        salt = b"auditronai_salt"  # Dans un cas réel, le salt devrait être unique et stocké de manière sécurisée
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key

    def _load_secrets(self) -> None:
        """Charge les secrets depuis le fichier chiffré."""
        if not self._secrets_file.exists():
            self._secrets = {}
            return

        try:
            encrypted_data = self._secrets_file.read_bytes()
            decrypted_data = self._fernet.decrypt(encrypted_data)
            self._secrets = json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des secrets: {e}")
            self._secrets = {}

    def _save_secrets(self) -> None:
        """Sauvegarde les secrets dans le fichier chiffré."""
        try:
            encrypted_data = self._fernet.encrypt(json.dumps(self._secrets).encode())
            self._secrets_file.write_bytes(encrypted_data)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des secrets: {e}")
            raise

    def get_secret(self, key: str, default: Any = None) -> Any:
        """Récupère un secret.
        
        Args:
            key: Clé du secret
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            La valeur du secret ou la valeur par défaut
        """
        return self._secrets.get(key, default)

    def set_secret(self, key: str, value: Any) -> None:
        """Définit un secret.
        
        Args:
            key: Clé du secret
            value: Valeur du secret
        """
        self._secrets[key] = value
        self._save_secrets()

    def delete_secret(self, key: str) -> None:
        """Supprime un secret.
        
        Args:
            key: Clé du secret à supprimer
        """
        if key in self._secrets:
            del self._secrets[key]
            self._save_secrets()

    def rotate_key(self) -> None:
        """Effectue une rotation de la clé de chiffrement."""
        new_key = self._generate_key()
        new_fernet = Fernet(new_key)
        
        # Rechiffre tous les secrets avec la nouvelle clé
        encrypted_data = self._fernet.encrypt(json.dumps(self._secrets).encode())
        decrypted_data = new_fernet.decrypt(encrypted_data)
        
        self._key = new_key
        self._fernet = new_fernet
        self._save_secrets()

    def clear_all(self) -> None:
        """Supprime tous les secrets."""
        self._secrets = {}
        if self._secrets_file.exists():
            self._secrets_file.unlink()

# Instance globale du gestionnaire de secrets
secrets_manager = SecretsManager() 