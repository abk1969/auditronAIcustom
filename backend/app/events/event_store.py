"""Implémentation du pattern Event Sourcing."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
from app.models.base import BaseModel

class Event(BaseModel):
    __tablename__ = "events"

    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    aggregate_type = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False)
    sequence = Column(Integer, nullable=False)

    @classmethod
    def create(cls, aggregate_id: uuid.UUID, aggregate_type: str, 
               event_type: str, data: Dict[str, Any], 
               metadata: Optional[Dict[str, Any]] = None) -> "Event":
        return cls(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_type=event_type,
            event_data=data,
            metadata=metadata or {},
            sequence=0  # Sera mis à jour par l'EventStore
        )

class EventStore:
    def __init__(self, session):
        self.session = session

    async def save_event(self, event: Event) -> None:
        # Obtenir la dernière séquence pour cet agrégat
        last_event = await self.session.query(Event)\
            .filter(Event.aggregate_id == event.aggregate_id)\
            .order_by(Event.sequence.desc())\
            .first()
        
        event.sequence = (last_event.sequence + 1) if last_event else 0
        self.session.add(event)
        await self.session.flush()

    async def get_events(self, aggregate_id: uuid.UUID) -> List[Event]:
        return await self.session.query(Event)\
            .filter(Event.aggregate_id == aggregate_id)\
            .order_by(Event.sequence)\
            .all() 