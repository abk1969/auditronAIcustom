"""Gestionnaire de dépôts de base."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.base import BaseModel
from app.schemas.base import PaginationParams
from app.core.monitoring import monitoring

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    """Dépôt de base pour tous les modèles."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialise le dépôt.
        
        Args:
            model: Type du modèle
        """
        self.model = model
    
    @monitoring.track_db_query()
    async def create(
        self,
        db: AsyncSession,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        """Crée un nouvel objet.
        
        Args:
            db: Session de base de données
            obj_in: Données de l'objet
            
        Returns:
            Objet créé
        """
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.dict(exclude_unset=True)
            
        db_obj = self.model(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    @monitoring.track_db_query()
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        """Met à jour un objet.
        
        Args:
            db: Session de base de données
            db_obj: Objet à mettre à jour
            obj_in: Données de mise à jour
            
        Returns:
            Objet mis à jour
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    @monitoring.track_db_query()
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
        obj = await self.get(db, id=id)
        if obj:
            if hasattr(obj, "soft_delete") and user_id:
                obj.soft_delete(user_id)
                db.add(obj)
            else:
                await db.delete(obj)
            await db.commit()
        return obj
    
    @monitoring.track_db_query()
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
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @monitoring.track_db_query()
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
        query = select(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
                    
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @monitoring.track_db_query()
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
        # Construit la requête de base
        query = select(self.model)
        
        # Applique les filtres
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
                    
        # Applique le tri
        if params.sort_by and hasattr(self.model, params.sort_by):
            sort_field = getattr(self.model, params.sort_by)
            if params.sort_order == "desc":
                sort_field = sort_field.desc()
            query = query.order_by(sort_field)
            
        # Compte le nombre total
        count_query = select(func.count()).select_from(query)
        total = await db.scalar(count_query)
        
        # Applique la pagination
        skip = (params.page - 1) * params.size
        query = query.offset(skip).limit(params.size)
        
        # Exécute la requête
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    @monitoring.track_db_query()
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
        query = select(self.model)
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
                
        result = await db.execute(query)
        return result.first() is not None
    
    def _prepare_query(
        self,
        query: Select,
        search_term: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        exclude_deleted: bool = True
    ) -> Select:
        """Prépare une requête avec filtres.
        
        Args:
            query: Requête de base
            search_term: Terme de recherche
            filters: Filtres à appliquer
            exclude_deleted: Exclure les objets supprimés
            
        Returns:
            Requête préparée
        """
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
                    
        if exclude_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))
            
        return query 