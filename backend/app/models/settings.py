"""Modèle de paramètres système."""
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
import enum
from .base import BaseModel

class SettingScope(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ANALYSIS = "analysis"
    SECURITY = "security"

class Setting(BaseModel):
    __tablename__ = "settings"

    key = Column(String, unique=True, nullable=False)
    value = Column(JSONB, nullable=False)
    scope = Column(Enum(SettingScope), nullable=False)
    description = Column(String, nullable=True)
    is_encrypted = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Setting {self.key} - {self.scope.value}>" 