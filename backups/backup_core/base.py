"""Base SQLAlchemy pour les modèles."""

from sqlalchemy.orm import declarative_base

# Déclaration de la classe Base pour les modèles SQLAlchemy
Base = declarative_base()

__all__ = ['Base'] 