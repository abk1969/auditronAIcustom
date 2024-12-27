"""Schémas utilisateur."""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID

from app.schemas.base import (
    BaseAPISchema,
    BaseAuditSchema,
    BaseCreateSchema,
    BaseUpdateSchema
)

class RoleBase(BaseModel):
    """Schéma de base pour les rôles."""
    
    name: str = Field(..., description="Nom du rôle")
    description: Optional[str] = Field(None, description="Description du rôle")
    permissions: List[str] = Field(default_factory=list, description="Permissions")

class RoleCreate(BaseCreateSchema, RoleBase):
    """Schéma de création de rôle."""
    
    pass

class RoleUpdate(BaseUpdateSchema, RoleBase):
    """Schéma de mise à jour de rôle."""
    
    name: Optional[str] = Field(None, description="Nom du rôle")
    permissions: Optional[List[str]] = Field(None, description="Permissions")

class Role(BaseAuditSchema, RoleBase):
    """Schéma de rôle complet."""
    
    pass

class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs."""
    
    email: EmailStr = Field(..., description="Adresse email")
    username: str = Field(..., min_length=3, description="Nom d'utilisateur")
    full_name: Optional[str] = Field(None, description="Nom complet")
    is_active: bool = Field(True, description="Compte actif")
    is_superuser: bool = Field(False, description="Super utilisateur")
    is_verified: bool = Field(False, description="Email vérifié")
    preferred_language: str = Field("fr", description="Langue préférée")
    notification_enabled: bool = Field(True, description="Notifications activées")
    theme: str = Field("light", description="Thème")

class UserCreate(BaseCreateSchema, UserBase):
    """Schéma de création d'utilisateur."""
    
    password: str = Field(
        ...,
        min_length=8,
        description="Mot de passe",
        example="motdepasse123"
    )
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Valide le mot de passe.
        
        Args:
            v: Mot de passe
            
        Returns:
            Mot de passe validé
            
        Raises:
            ValueError: Si le mot de passe est invalide
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir un chiffre")
        return v

class UserUpdate(BaseUpdateSchema, UserBase):
    """Schéma de mise à jour d'utilisateur."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator("password")
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Valide le mot de passe.
        
        Args:
            v: Mot de passe
            
        Returns:
            Mot de passe validé
            
        Raises:
            ValueError: Si le mot de passe est invalide
        """
        if v is not None:
            if len(v) < 8:
                raise ValueError("Le mot de passe doit contenir 8 caractères minimum")
            if not any(c.isupper() for c in v):
                raise ValueError("Le mot de passe doit contenir une majuscule")
            if not any(c.islower() for c in v):
                raise ValueError("Le mot de passe doit contenir une minuscule")
            if not any(c.isdigit() for c in v):
                raise ValueError("Le mot de passe doit contenir un chiffre")
        return v

class User(BaseAuditSchema, UserBase):
    """Schéma d'utilisateur complet."""
    
    roles: List[Role] = Field(default_factory=list, description="Rôles")
    mfa_enabled: bool = Field(False, description="MFA activé")

class UserInDB(User):
    """Schéma d'utilisateur en base de données."""
    
    hashed_password: str = Field(..., description="Mot de passe hashé")

class Token(BaseModel):
    """Schéma de token."""
    
    access_token: str = Field(..., description="Token d'accès")
    token_type: str = Field("bearer", description="Type de token")
    expires_in: int = Field(..., description="Expiration en secondes")
    refresh_token: Optional[str] = Field(None, description="Token de rafraîchissement")

class TokenPayload(BaseModel):
    """Schéma de payload de token."""
    
    sub: UUID = Field(..., description="ID utilisateur")
    exp: int = Field(..., description="Expiration")
    type: str = Field(..., description="Type de token")
    jti: UUID = Field(..., description="ID unique du token")

class ChangePassword(BaseModel):
    """Schéma de changement de mot de passe."""
    
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(
        ...,
        min_length=8,
        description="Nouveau mot de passe"
    )
    
    @validator("new_password")
    def validate_new_password(cls, v: str, values: dict) -> str:
        """Valide le nouveau mot de passe.
        
        Args:
            v: Nouveau mot de passe
            values: Valeurs du modèle
            
        Returns:
            Nouveau mot de passe validé
            
        Raises:
            ValueError: Si le mot de passe est invalide
        """
        if "current_password" in values and v == values["current_password"]:
            raise ValueError(
                "Le nouveau mot de passe doit être différent de l'ancien"
            )
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir un chiffre")
        return v

class ResetPassword(BaseModel):
    """Schéma de réinitialisation de mot de passe."""
    
    token: str = Field(..., description="Token de réinitialisation")
    new_password: str = Field(
        ...,
        min_length=8,
        description="Nouveau mot de passe"
    )
    
    @validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        """Valide le nouveau mot de passe.
        
        Args:
            v: Nouveau mot de passe
            
        Returns:
            Nouveau mot de passe validé
            
        Raises:
            ValueError: Si le mot de passe est invalide
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir une majuscule")
        if not any(c.islower() for c in v):
            raise ValueError("Le mot de passe doit contenir une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir un chiffre")
        return v 