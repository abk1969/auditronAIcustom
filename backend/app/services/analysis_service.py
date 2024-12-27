import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
import aiofiles
import aiohttp
from fastapi import UploadFile, HTTPException
from app.schemas.analysis import (
    Analysis,
    AnalysisStatus,
    CodeUploadRequest,
    GitRepositoryRequest,
    AnalysisIssue,
    AnalysisSuggestion
)

class AnalysisService:
    UPLOAD_DIR = "uploads"

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    async def create_analysis_from_upload(self, file: UploadFile, user_id: str) -> Analysis:
        """Crée une analyse à partir d'un fichier uploadé."""
        try:
            # Générer un ID unique pour l'analyse
            analysis_id = str(uuid.uuid4())
            
            # Créer le dossier pour cette analyse
            analysis_dir = os.path.join(self.UPLOAD_DIR, analysis_id)
            os.makedirs(analysis_dir, exist_ok=True)
            
            # Sauvegarder le fichier
            file_path = os.path.join(analysis_dir, file.filename)
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Détecter le langage (à implémenter)
            language = self._detect_language(file.filename)
            
            # Créer l'analyse
            analysis = Analysis(
                id=analysis_id,
                user_id=user_id,
                repository_name=file.filename,
                language=language,
                status=AnalysisStatus.PENDING,
                metrics={},
                issues=[],
                suggestions=[],
                summary="Analyse en cours",
                lines_of_code=0,
                complexity_score=0.0,
                security_score=0.0,
                performance_score=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Lancer l'analyse en arrière-plan (à implémenter)
            self._schedule_analysis(analysis_id, file_path)
            
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_analysis_from_repository(self, repo_request: GitRepositoryRequest, user_id: str) -> Analysis:
        """Crée une analyse à partir d'un dépôt Git."""
        try:
            # Générer un ID unique pour l'analyse
            analysis_id = str(uuid.uuid4())
            
            # Extraire le nom du dépôt de l'URL
            repo_name = self._extract_repo_name(str(repo_request.url))
            
            # Créer l'analyse
            analysis = Analysis(
                id=analysis_id,
                user_id=user_id,
                repository_url=str(repo_request.url),
                repository_name=repo_name,
                language="unknown",  # Sera détecté après le clone
                status=AnalysisStatus.PENDING,
                metrics={},
                issues=[],
                suggestions=[],
                summary="Analyse en cours",
                lines_of_code=0,
                complexity_score=0.0,
                security_score=0.0,
                performance_score=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Lancer l'analyse en arrière-plan (à implémenter)
            self._schedule_repository_analysis(analysis_id, str(repo_request.url), repo_request.branch)
            
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _detect_language(self, filename: str) -> str:
        """Détecte le langage à partir du nom de fichier."""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'c++',
            '.c': 'c',
            '.cs': 'c#',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        ext = os.path.splitext(filename)[1].lower()
        return extensions.get(ext, 'unknown')

    def _extract_repo_name(self, url: str) -> str:
        """Extrait le nom du dépôt de l'URL Git."""
        try:
            # Pour GitHub: https://github.com/username/repo
            parts = url.rstrip('/').split('/')
            return parts[-1]
        except:
            return "unknown-repo"

    def _schedule_analysis(self, analysis_id: str, file_path: str):
        """Programme l'analyse en arrière-plan."""
        # TODO: Implémenter l'analyse asynchrone
        pass

    def _schedule_repository_analysis(self, analysis_id: str, repo_url: str, branch: Optional[str]):
        """Programme l'analyse d'un dépôt en arrière-plan."""
        # TODO: Implémenter l'analyse asynchrone
        pass

analysis_service = AnalysisService() 