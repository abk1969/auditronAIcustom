"""Factory pour la création des repositories."""
from typing import Type, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.base import BaseModel

class RepositoryFactory:
    _repositories: Dict[Type[BaseModel], Type[BaseRepository]] = {}

    @classmethod
    def register(cls, model: Type[BaseModel], repository: Type[BaseRepository]):
        cls._repositories[model] = repository

    @classmethod
    def get(cls, model: Type[BaseModel], session: Session) -> BaseRepository:
        repository_class = cls._repositories.get(model)
        if not repository_class:
            raise ValueError(f"No repository registered for model {model.__name__}")
        return repository_class(model, session) 