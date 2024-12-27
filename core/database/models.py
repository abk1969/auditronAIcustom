"""
Modèles SQLAlchemy pour la base de données.
Définit la structure des tables et leurs relations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """Modèle pour la table des utilisateurs."""
    __tablename__ = 'users'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="created_by_user")
    api_tokens = relationship("ApiToken", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStat", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    """Modèle pour la table des projets."""
    __tablename__ = 'projects'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    repository_url = Column(String(512))
    is_public = Column(Boolean, default=False)

    # Relations
    owner = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    analyzer_configs = relationship("AnalyzerConfig", back_populates="project", cascade="all, delete-orphan")

class Analysis(Base):
    """Modèle pour la table des analyses."""
    __tablename__ = 'analyses'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    project_id = Column(PostgresUUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50), nullable=False)
    result_summary = Column(JSONB)
    configuration = Column(JSONB)
    created_by = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id'))

    # Relations
    project = relationship("Project", back_populates="analyses")
    created_by_user = relationship("User", back_populates="analyses")
    results = relationship("AnalysisResult", back_populates="analysis", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")

class AnalysisResult(Base):
    """Modèle pour la table des résultats d'analyse détaillés."""
    __tablename__ = 'analysis_results'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    analysis_id = Column(PostgresUUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'))
    analyzer_name = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    line_number = Column(Integer)
    column_number = Column(Integer)
    message = Column(Text, nullable=False)
    code_snippet = Column(Text)
    rule_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    analysis = relationship("Analysis", back_populates="results")

class Metric(Base):
    """Modèle pour la table des métriques."""
    __tablename__ = 'metrics'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    analysis_id = Column(PostgresUUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    analysis = relationship("Analysis", back_populates="metrics")

class Report(Base):
    """Modèle pour la table des rapports."""
    __tablename__ = 'reports'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    analysis_id = Column(PostgresUUID(as_uuid=True), ForeignKey('analyses.id', ondelete='CASCADE'))
    format = Column(String(50), nullable=False)
    content = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    analysis = relationship("Analysis", back_populates="reports")

class AnalyzerConfig(Base):
    """Modèle pour la table des configurations d'analyseur."""
    __tablename__ = 'analyzer_configs'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    project_id = Column(PostgresUUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'))
    analyzer_name = Column(String(100), nullable=False)
    configuration = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    project = relationship("Project", back_populates="analyzer_configs")

class UsageStat(Base):
    """Modèle pour la table des statistiques d'utilisation."""
    __tablename__ = 'usage_stats'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    action_type = Column(String(100), nullable=False)
    action_details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="usage_stats")

class ApiToken(Base):
    """Modèle pour la table des tokens d'API."""
    __tablename__ = 'api_tokens'

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    token = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))

    # Relations
    user = relationship("User", back_populates="api_tokens")
