"""Utilitaires de gestion des mots de passe."""

from passlib.context import CryptContext

# Contexte de hachage des mots de passe
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Mot de passe haché
        
    Returns:
        True si le mot de passe est valide
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe.
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Mot de passe haché
    """
    return pwd_context.hash(password) 