"""Validateur d'entrées sécurisé pour AuditronAI."""

import re
from typing import Any, List, Optional, Pattern
from pathlib import Path
import magic
from pydantic import BaseModel, validator
from .security_config import security_settings

class SecurityValidationError(Exception):
    """Exception pour les erreurs de validation de sécurité."""
    pass

class InputValidator:
    """Validateur d'entrées avec règles de sécurité strictes."""

    # Expressions régulières de sécurité
    SQL_INJECTION_PATTERN: Pattern = re.compile(
        r"(?i)(select|insert|update|delete|drop|union|exec|\-\-|\/\*|\*\/|;|\@|\$|#)"
    )
    XSS_PATTERN: Pattern = re.compile(
        r"(?i)(<script|javascript:|data:|vbscript:|onload=|onerror=)"
    )
    PATH_TRAVERSAL_PATTERN: Pattern = re.compile(r"\.{2,}\/|\.{2,}\\")
    COMMAND_INJECTION_PATTERN: Pattern = re.compile(
        r"(?i)(&|\||;|\$\(|\`|\${|eval\(|system\()"
    )

    @classmethod
    def validate_string_input(cls, value: str, max_length: Optional[int] = None) -> str:
        """Valide une entrée string.
        
        Args:
            value: Valeur à valider
            max_length: Longueur maximale autorisée
        
        Returns:
            La valeur validée
            
        Raises:
            SecurityValidationError: Si la validation échoue
        """
        if not isinstance(value, str):
            raise SecurityValidationError("L'entrée doit être une chaîne de caractères")

        max_length = max_length or security_settings.INPUT_MAX_LENGTH
        if len(value) > max_length:
            raise SecurityValidationError(f"L'entrée dépasse la longueur maximale de {max_length}")

        if cls.SQL_INJECTION_PATTERN.search(value):
            raise SecurityValidationError("Motif d'injection SQL détecté")

        if cls.XSS_PATTERN.search(value):
            raise SecurityValidationError("Motif XSS détecté")

        if cls.COMMAND_INJECTION_PATTERN.search(value):
            raise SecurityValidationError("Motif d'injection de commande détecté")

        return value

    @classmethod
    def validate_file_path(cls, path: str) -> Path:
        """Valide un chemin de fichier.
        
        Args:
            path: Chemin à valider
        
        Returns:
            Le chemin validé
            
        Raises:
            SecurityValidationError: Si la validation échoue
        """
        if cls.PATH_TRAVERSAL_PATTERN.search(path):
            raise SecurityValidationError("Tentative de traversée de répertoire détectée")

        try:
            path_obj = Path(path).resolve()
            if not path_obj.suffix.lower() in security_settings.ALLOWED_FILE_EXTENSIONS:
                raise SecurityValidationError("Extension de fichier non autorisée")
            return path_obj
        except Exception as e:
            raise SecurityValidationError(f"Chemin de fichier invalide: {e}")

    @classmethod
    def validate_file_content(cls, content: bytes, filename: str) -> bytes:
        """Valide le contenu d'un fichier.
        
        Args:
            content: Contenu du fichier
            filename: Nom du fichier
        
        Returns:
            Le contenu validé
            
        Raises:
            SecurityValidationError: Si la validation échoue
        """
        if len(content) > security_settings.FILE_UPLOAD_MAX_SIZE:
            raise SecurityValidationError("Taille de fichier dépassée")

        mime = magic.from_buffer(content, mime=True)
        if mime not in [
            "text/plain",
            "text/x-python",
            "text/javascript",
            "application/x-sql",
            "text/x-typescript"
        ]:
            raise SecurityValidationError(f"Type MIME non autorisé: {mime}")

        return content

    @classmethod
    def sanitize_html(cls, html: str) -> str:
        """Nettoie le HTML des balises dangereuses.
        
        Args:
            html: HTML à nettoyer
        
        Returns:
            Le HTML nettoyé
        """
        # Utilisation d'une liste blanche de balises autorisées
        ALLOWED_TAGS = {
            "p", "br", "strong", "em", "u", "ol", "ul", "li",
            "h1", "h2", "h3", "h4", "h5", "h6", "code", "pre"
        }
        
        # Supprime toutes les balises non autorisées
        cleaned = re.sub(r"<[^>]+>", lambda match: match.group(0)
            if any(tag in match.group(0).lower() for tag in ALLOWED_TAGS)
            else "", html)
        
        # Supprime les attributs dangereux
        cleaned = re.sub(r"(?i)(javascript|onerror|onload|onclick|onmouseover):", "", cleaned)
        
        return cleaned

    @classmethod
    def validate_json_structure(cls, data: Any, required_fields: List[str]) -> None:
        """Valide la structure d'un JSON.
        
        Args:
            data: Données à valider
            required_fields: Champs requis
            
        Raises:
            SecurityValidationError: Si la validation échoue
        """
        if not isinstance(data, dict):
            raise SecurityValidationError("Les données doivent être un dictionnaire")

        for field in required_fields:
            if field not in data:
                raise SecurityValidationError(f"Champ requis manquant: {field}")

        for key, value in data.items():
            if isinstance(value, str):
                cls.validate_string_input(value)

# Instance globale du validateur
input_validator = InputValidator() 