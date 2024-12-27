"""Modèle d'analyse de code."""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class AnalysisStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Analysis(BaseModel):
    __tablename__ = "analyses"

    user_id = Column(ForeignKey("users.id"), nullable=False)
    repository_url = Column(String, nullable=True)
    code_snippet = Column(Text, nullable=True)
    language = Column(String, nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Métriques d'analyse
    metrics = Column(JSONB, default={}, nullable=False)
    issues = Column(ARRAY(JSONB), default=[], nullable=False)
    suggestions = Column(ARRAY(JSONB), default=[], nullable=False)
    
    # Statistiques
    lines_of_code = Column(Integer, default=0)
    complexity_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    
    # Relations
    user = relationship("User", backref="analyses")
    reports = relationship("AnalysisReport", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<Analysis {self.id} - {self.status.value}>" 