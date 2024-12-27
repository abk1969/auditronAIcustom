"""Modèle utilisateur."""

from typing import List, Optional
from sqlalchemy import Boolean, Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.models.base import BaseAuditModel
from app.core.security.password import get_password_hash

class User(BaseAuditModel):
    """Modèle utilisateur."""
    
    # Informations de base
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    
    # Statut et sécurité
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    
    # Authentification multi-facteur
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)
    backup_codes = Column(ARRAY(String), nullable=True)
    
    # Préférences
    preferred_language = Column(String, default="fr")
    notification_enabled = Column(Boolean, default=True)
    theme = Column(String, default="light")
    
    # Relations
    roles = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users"
    )
    
    def __init__(self, **kwargs):
        """Initialise l'utilisateur.
        
        Args:
            **kwargs: Attributs de l'utilisateur
        """
        if "password" in kwargs:
            kwargs["hashed_password"] = get_password_hash(kwargs.pop("password"))
        super().__init__(**kwargs)
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur.
        
        Returns:
            True si administrateur
        """
        return self.is_superuser or any(
            role.name == "admin" for role in self.roles
        )
    
    def has_role(self, role_name: str) -> bool:
        """Vérifie si l'utilisateur a un rôle.
        
        Args:
            role_name: Nom du rôle
            
        Returns:
            True si l'utilisateur a le rôle
        """
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission: str) -> bool:
        """Vérifie si l'utilisateur a une permission.
        
        Args:
            permission: Permission à vérifier
            
        Returns:
            True si l'utilisateur a la permission
        """
        if self.is_superuser:
            return True
            
        return any(
            permission in role.permissions
            for role in self.roles
        )

class Role(BaseAuditModel):
    """Modèle de rôle."""
    
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    permissions = Column(ARRAY(String), nullable=False, default=list)
    
    # Relations
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )

# Table de liaison utilisateurs-rôles
user_roles = Table(
    "user_roles",
    BaseAuditModel.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )
) 