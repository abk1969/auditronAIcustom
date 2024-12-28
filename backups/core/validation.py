"""Gestionnaire de validation."""

import re
from typing import Any, Dict, List, Optional, Pattern, Union
from urllib.parse import urlparse

from pydantic import BaseModel, EmailStr, validator

from app.core.logging import get_logger

logger = get_logger(__name__)

class ValidationManager:
    """Gestionnaire de validation."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        # Expressions régulières
        self.email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        self.phone_regex = re.compile(r"^\+?1?\d{9,15}$")
        self.username_regex = re.compile(r"^[a-zA-Z0-9_-]{3,16}$")
        self.password_regex = re.compile(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        )
        self.url_regex = re.compile(
            r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\."
            r"[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
        )
        
        # Expressions SQL dangereuses
        self.sql_patterns = [
            r"(?i)(\bSELECT\b.*\bFROM\b|\bINSERT\b.*\bINTO\b|\bUPDATE\b|\bDELETE\b.*\bFROM\b)",
            r"(?i)(\bDROP\b|\bTRUNCATE\b|\bALTER\b|\bCREATE\b|\bREPLACE\b)",
            r"(?i)(\bUNION\b.*\bSELECT\b|\bEXEC\b|\bEXECUTE\b)",
            r"--",
            r";",
            r"\/\*.*?\*\/"
        ]
        
        # Expressions XSS dangereuses
        self.xss_patterns = [
            r"<script.*?>.*?<\/script>",
            r"javascript:",
            r"onerror=",
            r"onload=",
            r"onclick=",
            r"onmouseover=",
            r"eval\(",
            r"document\.",
            r"window\."
        ]
        
        # Expressions d'injection de commandes
        self.cmd_patterns = [
            r"[&|;`]",
            r"\$\(",
            r"\b(cat|grep|echo|ls|pwd|cd|rm|cp|mv|chmod|chown|wget|curl)\b"
        ]
        
        # Expressions de traversée de chemin
        self.path_patterns = [
            r"\.\.",
            r"~",
            r"%2e",
            r"%2f"
        ]
    
    def validate_email(self, email: str) -> bool:
        """Valide une adresse email.
        
        Args:
            email: Adresse email
            
        Returns:
            True si valide
        """
        return bool(self.email_regex.match(email))
    
    def validate_phone(self, phone: str) -> bool:
        """Valide un numéro de téléphone.
        
        Args:
            phone: Numéro de téléphone
            
        Returns:
            True si valide
        """
        return bool(self.phone_regex.match(phone))
    
    def validate_username(self, username: str) -> bool:
        """Valide un nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            True si valide
        """
        return bool(self.username_regex.match(username))
    
    def validate_password(self, password: str) -> bool:
        """Valide un mot de passe.
        
        Args:
            password: Mot de passe
            
        Returns:
            True si valide
        """
        return bool(self.password_regex.match(password))
    
    def validate_url(self, url: str) -> bool:
        """Valide une URL.
        
        Args:
            url: URL
            
        Returns:
            True si valide
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def check_sql_injection(self, value: str) -> bool:
        """Vérifie la présence d'injection SQL.
        
        Args:
            value: Valeur à vérifier
            
        Returns:
            True si sûr
        """
        return not any(
            bool(re.search(pattern, value))
            for pattern in self.sql_patterns
        )
    
    def check_xss(self, value: str) -> bool:
        """Vérifie la présence de XSS.
        
        Args:
            value: Valeur à vérifier
            
        Returns:
            True si sûr
        """
        return not any(
            bool(re.search(pattern, value))
            for pattern in self.xss_patterns
        )
    
    def check_command_injection(self, value: str) -> bool:
        """Vérifie la présence d'injection de commandes.
        
        Args:
            value: Valeur à vérifier
            
        Returns:
            True si sûr
        """
        return not any(
            bool(re.search(pattern, value))
            for pattern in self.cmd_patterns
        )
    
    def check_path_traversal(self, value: str) -> bool:
        """Vérifie la présence de traversée de chemin.
        
        Args:
            value: Valeur à vérifier
            
        Returns:
            True si sûr
        """
        return not any(
            bool(re.search(pattern, value))
            for pattern in self.path_patterns
        )
    
    def sanitize_html(self, value: str) -> str:
        """Nettoie le HTML.
        
        Args:
            value: Valeur à nettoyer
            
        Returns:
            Valeur nettoyée
        """
        # TODO: Implémenter le nettoyage HTML
        pass
    
    def validate_json(self, value: Any) -> bool:
        """Valide une structure JSON.
        
        Args:
            value: Valeur à valider
            
        Returns:
            True si valide
        """
        try:
            if isinstance(value, (dict, list)):
                return True
            return False
        except Exception:
            return False
    
    def validate_file_type(self, filename: str, allowed_types: List[str]) -> bool:
        """Valide le type d'un fichier.
        
        Args:
            filename: Nom du fichier
            allowed_types: Types autorisés
            
        Returns:
            True si valide
        """
        return any(filename.lower().endswith(ext) for ext in allowed_types)
    
    def validate_file_size(self, size: int, max_size: int) -> bool:
        """Valide la taille d'un fichier.
        
        Args:
            size: Taille du fichier
            max_size: Taille maximale
            
        Returns:
            True si valide
        """
        return size <= max_size
    
    def validate_date_format(self, date: str, format: str) -> bool:
        """Valide le format d'une date.
        
        Args:
            date: Date à valider
            format: Format attendu
            
        Returns:
            True si valide
        """
        try:
            from datetime import datetime
            datetime.strptime(date, format)
            return True
        except ValueError:
            return False

# Instance globale
validation_manager = ValidationManager() 