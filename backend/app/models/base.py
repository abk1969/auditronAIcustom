"""Modèles de base."""

from datetime import datetime
from typing import Any, Dict
import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr

from app.core.base import Base

class BaseModel(Base):
    """Modèle de base pour tous les modèles."""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Nom de la table en minuscules."""
        return cls.__name__.lower()
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire.
        
        Returns:
            Dictionnaire des attributs
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        
    def update(self, **kwargs: Any) -> None:
        """Met à jour les attributs du modèle.
        
        Args:
            **kwargs: Attributs à mettre à jour
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class BaseAuditModel(BaseModel):
    """Modèle de base avec audit."""
    
    __abstract__ = True
    
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    
    @property
    def is_deleted(self) -> bool:
        """Vérifie si le modèle est supprimé.
        
        Returns:
            True si supprimé
        """
        return self.deleted_at is not None
        
    def soft_delete(self, user_id: uuid.UUID) -> None:
        """Supprime le modèle de manière douce.
        
        Args:
            user_id: ID de l'utilisateur
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        
    def restore(self) -> None:
        """Restaure le modèle."""
        self.deleted_at = None
        self.deleted_by = None

class BaseVersionedModel(BaseAuditModel):
    """Modèle de base avec versionnement."""
    
    __abstract__ = True
    
    version = Column(String, nullable=False)
    previous_version = Column(UUID(as_uuid=True), nullable=True)
    
    def create_version(self, user_id: uuid.UUID) -> "BaseVersionedModel":
        """Crée une nouvelle version du modèle.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Nouvelle version
        """
        # Crée une copie du modèle
        new_version = self.__class__()
        
        # Copie les attributs
        for column in self.__table__.columns:
            if column.name not in {
                "id",
                "created_at",
                "updated_at",
                "version",
                "previous_version"
            }:
                setattr(new_version, column.name, getattr(self, column.name))
                
        # Met à jour les métadonnées
        new_version.previous_version = self.id
        new_version.version = str(uuid.uuid4())
        new_version.created_by = user_id
        new_version.updated_by = user_id
        
        return new_version 