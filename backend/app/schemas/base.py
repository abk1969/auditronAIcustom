"""Schémas de base."""

from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, validator
from pydantic.generics import GenericModel

# Type variable pour les modèles génériques
ModelType = TypeVar("ModelType")

class BaseSchema(BaseModel):
    """Schéma de base pour tous les schémas."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )

class BaseAPISchema(BaseSchema):
    """Schéma de base pour les réponses API."""
    
    id: UUID = Field(..., description="Identifiant unique")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")

class BaseAuditSchema(BaseAPISchema):
    """Schéma de base avec audit."""
    
    created_by: Optional[UUID] = Field(None, description="Créé par")
    updated_by: Optional[UUID] = Field(None, description="Mis à jour par")
    deleted_at: Optional[datetime] = Field(None, description="Date de suppression")
    deleted_by: Optional[UUID] = Field(None, description="Supprimé par")
    
    @property
    def is_deleted(self) -> bool:
        """Vérifie si l'objet est supprimé."""
        return self.deleted_at is not None

class BaseVersionedSchema(BaseAuditSchema):
    """Schéma de base avec versionnement."""
    
    version: str = Field(..., description="Version")
    previous_version: Optional[UUID] = Field(
        None,
        description="Version précédente"
    )

class BaseCreateSchema(BaseSchema):
    """Schéma de base pour la création."""
    
    pass

class BaseUpdateSchema(BaseSchema):
    """Schéma de base pour la mise à jour."""
    
    pass

class BaseResponse(GenericModel, Generic[ModelType]):
    """Réponse API générique."""
    
    success: bool = Field(..., description="Succès de l'opération")
    message: Optional[str] = Field(None, description="Message")
    data: Optional[ModelType] = Field(None, description="Données")
    errors: Optional[Dict[str, Any]] = Field(None, description="Erreurs")

class PaginationParams(BaseSchema):
    """Paramètres de pagination."""
    
    page: int = Field(1, ge=1, description="Numéro de page")
    size: int = Field(10, ge=1, le=100, description="Taille de la page")
    sort_by: Optional[str] = Field(None, description="Champ de tri")
    sort_order: Optional[str] = Field(
        None,
        description="Ordre de tri (asc/desc)"
    )
    
    @validator("sort_order")
    def validate_sort_order(cls, v: Optional[str]) -> Optional[str]:
        """Valide l'ordre de tri.
        
        Args:
            v: Ordre de tri
            
        Returns:
            Ordre de tri validé
            
        Raises:
            ValueError: Si l'ordre de tri est invalide
        """
        if v is not None and v.lower() not in {"asc", "desc"}:
            raise ValueError("L'ordre de tri doit être 'asc' ou 'desc'")
        return v.lower() if v else None

class PaginatedResponse(BaseResponse[ModelType]):
    """Réponse API paginée."""
    
    total: int = Field(..., description="Nombre total d'éléments")
    page: int = Field(..., description="Numéro de page actuel")
    size: int = Field(..., description="Taille de la page")
    pages: int = Field(..., description="Nombre total de pages")
    has_next: bool = Field(..., description="Page suivante disponible")
    has_prev: bool = Field(..., description="Page précédente disponible")
    
    @validator("pages")
    def validate_pages(cls, v: int, values: Dict[str, Any]) -> int:
        """Calcule le nombre total de pages.
        
        Args:
            v: Nombre de pages
            values: Valeurs du modèle
            
        Returns:
            Nombre de pages calculé
        """
        if "total" in values and "size" in values:
            return (values["total"] + values["size"] - 1) // values["size"]
        return v
        
    @validator("has_next")
    def validate_has_next(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Vérifie s'il y a une page suivante.
        
        Args:
            v: A une page suivante
            values: Valeurs du modèle
            
        Returns:
            True s'il y a une page suivante
        """
        if all(k in values for k in ["page", "pages"]):
            return values["page"] < values["pages"]
        return v
        
    @validator("has_prev")
    def validate_has_prev(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Vérifie s'il y a une page précédente.
        
        Args:
            v: A une page précédente
            values: Valeurs du modèle
            
        Returns:
            True s'il y a une page précédente
        """
        if "page" in values:
            return values["page"] > 1
        return v 