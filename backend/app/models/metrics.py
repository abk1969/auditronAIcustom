"""Modèle de métriques système."""
from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class MetricType(enum.Enum):
    SYSTEM = "system"
    APPLICATION = "application"
    CUSTOM = "custom"

class Metric(BaseModel):
    __tablename__ = "metrics"

    name = Column(String, nullable=False)
    type = Column(Enum(MetricType), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)
    
    # Pour les métriques liées à une analyse spécifique
    analysis_id = Column(ForeignKey("analyses.id"), nullable=True)
    analysis = relationship("Analysis", backref="related_metrics")

    def __repr__(self) -> str:
        return f"<Metric {self.name} - {self.value}{self.unit or ''}>" 