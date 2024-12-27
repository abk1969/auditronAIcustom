"""
Gestionnaire de fichiers temporaires sécurisé pour AuditronAI.
"""
import os
import tempfile
from contextlib import contextmanager
from typing import Generator
import secrets
from pathlib import Path

class TempFileManager:
    """Gestionnaire sécurisé pour les fichiers temporaires."""
    
    def __init__(self):
        """Initialise le gestionnaire avec un répertoire temporaire dédié."""
        self.temp_dir = Path(tempfile.gettempdir()) / f"auditronai_{secrets.token_hex(8)}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.temp_dir, 0o700)  # Permissions restrictives
        
    def cleanup(self):
        """Nettoie tous les fichiers temporaires."""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                try:
                    file.unlink()
                except Exception:
                    pass
            try:
                self.temp_dir.rmdir()
            except Exception:
                pass

    @contextmanager
    def temp_file(self, suffix: str = '.py', content: str = "") -> Generator[Path, None, None]:
        """
        Crée un fichier temporaire sécurisé.
        
        Args:
            suffix: Extension du fichier
            content: Contenu initial du fichier
            
        Yields:
            Path: Chemin vers le fichier temporaire
        """
        temp_path = self.temp_dir / f"temp_{secrets.token_hex(8)}{suffix}"
        try:
            temp_path.write_text(content, encoding='utf-8')
            os.chmod(temp_path, 0o600)  # Permissions restrictives
            yield temp_path
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
