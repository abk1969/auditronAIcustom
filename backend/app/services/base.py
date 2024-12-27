"""Gestionnaire de services de base."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel
from app.repositories.base import BaseRepository
from app.schemas.base import (
    BaseCreateSchema,
    BaseUpdateSchema,
    PaginationParams
)
from app.core.events import Event, event_bus
from app.core.logging import get_logger

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseCreateSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseUpdateSchema)

logger = get_logger(__name__)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Service de base pour tous les modèles."""
    
    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType]
    ):
        """Initialise le service.
        
        Args:
            model: Type du modèle
            create_schema: Schéma de création
            update_schema: Schéma de mise à jour
        """
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.repository = BaseRepository(model)
        
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
        user_id: Optional[UUID] = None
    ) -> ModelType:
        """Crée un nouvel objet.
        
        Args:
            db: Session de base de données
            obj_in: Données de l'objet
            user_id: ID de l'utilisateur
            
        Returns:
            Objet créé
        """
        create_data = obj_in.dict(exclude_unset=True)
        
        if user_id and hasattr(self.model, "created_by"):
            create_data["created_by"] = user_id
            
        try:
            db_obj = await self.repository.create(db, create_data)
            
            # Publie l'événement de création
            await event_bus.publish_async(Event(
                type=f"{self.model.__name__.lower()}.created",
                data={
                    "id": str(db_obj.id),
                    "user_id": str(user_id) if user_id else None
                }
            ))
            
            return db_obj
            
        except Exception as e:
            logger.error(
                f"Erreur lors de la création de {self.model.__name__}",
                extra={
                    "error": str(e),
                    "data": create_data
                }
            )
            raise
            
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        user_id: Optional[UUID] = None
    ) -> ModelType:
        """Met à jour un objet.
        
        Args:
            db: Session de base de données
            db_obj: Objet à mettre à jour
            obj_in: Données de mise à jour
            user_id: ID de l'utilisateur
            
        Returns:
            Objet mis à jour
        """
        update_data = (
            obj_in if isinstance(obj_in, dict)
            else obj_in.dict(exclude_unset=True)
        )
        
        if user_id and hasattr(self.model, "updated_by"):
            update_data["updated_by"] = user_id
            
        try:
            db_obj = await self.repository.update(
                db,
                db_obj=db_obj,
                obj_in=update_data
            )
            
            # Publie l'événement de mise à jour
            await event_bus.publish_async(Event(
                type=f"{self.model.__name__.lower()}.updated",
                data={
                    "id": str(db_obj.id),
                    "user_id": str(user_id) if user_id else None,
                    "changes": update_data
                }
            ))
            
            return db_obj
            
        except Exception as e:
            logger.error(
                f"Erreur lors de la mise à jour de {self.model.__name__}",
                extra={
                    "error": str(e),
                    "id": str(db_obj.id),
                    "data": update_data
                }
            )
            raise
            
    async def delete(
        self,
        db: AsyncSession,
        *,
        id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[ModelType]:
        """Supprime un objet.
        
        Args:
            db: Session de base de données
            id: ID de l'objet
            user_id: ID de l'utilisateur
            
        Returns:
            Objet supprimé
        """
        try:
            db_obj = await self.repository.delete(
                db,
                id=id,
                user_id=user_id
            )
            
            if db_obj:
                # Publie l'événement de suppression
                await event_bus.publish_async(Event(
                    type=f"{self.model.__name__.lower()}.deleted",
                    data={
                        "id": str(id),
                        "user_id": str(user_id) if user_id else None
                    }
                ))
                
            return db_obj
            
        except Exception as e:
            logger.error(
                f"Erreur lors de la suppression de {self.model.__name__}",
                extra={
                    "error": str(e),
                    "id": str(id)
                }
            )
            raise
            
    async def get(
        self,
        db: AsyncSession,
        id: UUID
    ) -> Optional[ModelType]:
        """Récupère un objet par son ID.
        
        Args:
            db: Session de base de données
            id: ID de l'objet
            
        Returns:
            Objet trouvé
        """
        try:
            return await self.repository.get(db, id=id)
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération de {self.model.__name__}",
                extra={
                    "error": str(e),
                    "id": str(id)
                }
            )
            raise
            
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Récupère plusieurs objets.
        
        Args:
            db: Session de base de données
            skip: Nombre d'objets à sauter
            limit: Nombre d'objets maximum
            filters: Filtres à appliquer
            
        Returns:
            Liste d'objets
        """
        try:
            return await self.repository.get_multi(
                db,
                skip=skip,
                limit=limit,
                filters=filters
            )
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération de {self.model.__name__}s",
                extra={
                    "error": str(e),
                    "skip": skip,
                    "limit": limit,
                    "filters": filters
                }
            )
            raise
            
    async def get_multi_paginated(
        self,
        db: AsyncSession,
        *,
        params: PaginationParams,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[ModelType], int]:
        """Récupère plusieurs objets avec pagination.
        
        Args:
            db: Session de base de données
            params: Paramètres de pagination
            filters: Filtres à appliquer
            
        Returns:
            Tuple (liste d'objets, nombre total)
        """
        try:
            return await self.repository.get_multi_paginated(
                db,
                params=params,
                filters=filters
            )
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération paginée de {self.model.__name__}s",
                extra={
                    "error": str(e),
                    "params": params.dict(),
                    "filters": filters
                }
            )
            raise
            
    async def exists(
        self,
        db: AsyncSession,
        **kwargs: Any
    ) -> bool:
        """Vérifie si un objet existe.
        
        Args:
            db: Session de base de données
            **kwargs: Critères de recherche
            
        Returns:
            True si l'objet existe
        """
        try:
            return await self.repository.exists(db, **kwargs)
        except Exception as e:
            logger.error(
                f"Erreur lors de la vérification de {self.model.__name__}",
                extra={
                    "error": str(e),
                    "criteria": kwargs
                }
            )
            raise 