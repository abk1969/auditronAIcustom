"""Gestionnaire d'événements de la base de données."""
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from app.models.base import BaseModel

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure les paramètres de connexion PostgreSQL."""
    cursor = dbapi_connection.cursor()
    cursor.execute("SET timezone='UTC'")
    cursor.close()

@event.listens_for(Session, 'before_flush')
def before_flush(session: Session, flush_context: Any, instances: Any) -> None:
    """Gère les événements avant le flush de la session."""
    for instance in session.new:
        if isinstance(instance, BaseModel):
            instance.created_at = datetime.utcnow()
            instance.updated_at = datetime.utcnow()

    for instance in session.dirty:
        if isinstance(instance, BaseModel):
            instance.updated_at = datetime.utcnow() 