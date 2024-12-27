"""Schémas de validation pour les analyses."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, constr, validator, HttpUrl
from datetime import datetime
from app.models.analysis import AnalysisStatus, AnalysisSeverity
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CodeUploadRequest(BaseModel):
    file_content: bytes
    filename: str
    language: Optional[str] = None

class GitRepositoryRequest(BaseModel):
    url: HttpUrl
    branch: Optional[str] = None

class AnalysisIssue(BaseModel):
    type: str
    severity: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    file: Optional[str] = None
    code: Optional[str] = None
    suggestion: Optional[str] = None

class AnalysisSuggestion(BaseModel):
    type: str
    message: str
    code: Optional[str] = None
    impact: Optional[str] = None
    effort: Optional[str] = None

class Analysis(BaseModel):
    id: str
    user_id: str
    repository_url: Optional[str] = None
    repository_name: str
    code_snippet: Optional[str] = None
    language: str
    status: AnalysisStatus
    metrics: Dict[str, Any]
    issues: List[AnalysisIssue]
    suggestions: List[AnalysisSuggestion]
    summary: str
    lines_of_code: int
    complexity_score: float
    security_score: float
    performance_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AnalysisResponse(BaseModel):
    success: bool
    data: Analysis
    message: Optional[str] = None

class AnalysisListResponse(BaseModel):
    success: bool
    data: List[Analysis]
    message: Optional[str] = None

class AnalysisStats(BaseModel):
    total_scans: int
    issues_found: int
    issues_resolved: int
    average_resolution_time: str

class AnalysisStatsResponse(BaseModel):
    success: bool
    data: AnalysisStats
    message: Optional[str] = None 