"""
Gestionnaire d'authentification pour AuditronAI.
"""

import bcrypt
from sqlalchemy.orm import Session
from core.database.models import User

class AuthManager:
    """Gestionnaire d'authentification."""

    def __init__(self, db: Session):
        """
        Initialise le gestionnaire d'authentification.
        
        Args:
            db: Session SQLAlchemy
        """
        self.db = db

    def register_user(self, email: str, password: str, first_name: str, last_name: str) -> User:
        """
        Enregistre un nouvel utilisateur.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            first_name: Prénom
            last_name: Nom
            
        Returns:
            User: L'utilisateur créé
            
        Raises:
            ValueError: Si l'email existe déjà
        """
        # Vérifier si l'email existe déjà
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Un utilisateur avec cet email existe déjà")

        # Hasher le mot de passe
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Créer l'utilisateur
        user = User(
            email=email,
            password_hash=password_hash.decode('utf-8'),
            first_name=first_name,
            last_name=last_name
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(self, email: str, password: str) -> tuple[bool, str, User | None]:
        """
        Authentifie un utilisateur.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            tuple: (succès, message, utilisateur)
        """
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            return False, "Email ou mot de passe incorrect", None

        if not user.is_active:
            return False, "Compte désactivé", None

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return True, "Authentification réussie", user
        
        return False, "Email ou mot de passe incorrect", None
