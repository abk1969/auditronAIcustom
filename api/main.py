"""API REST avec FastAPI."""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta

from ..core.security_analyzer import SecurityAnalyzer
from ..core.rate_limiter import RateLimiter
from ..core.resource_manager import ResourceManager
from ..core.queue.analysis_queue import AnalysisQueue
from ..core.metrics.prometheus_metrics import track_analysis
from ..core.logger import logger

app = FastAPI(
    title="AuditronAI API",
    description="API REST pour l'analyse de code",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances des services
analyzer = SecurityAnalyzer()
rate_limiter = RateLimiter()
resource_manager = ResourceManager()
analysis_queue = AnalysisQueue()

async def check_limits(client_id: str = "anonymous"):
    """Vérifie les limites de débit."""
    if not await rate_limiter.check_rate_limit(client_id, 'api'):
        raise HTTPException(429, "Trop de requêtes")
    if not resource_manager.check_resources('analysis'):
        raise HTTPException(503, "Ressources insuffisantes")

@app.get("/analysis")
async def get_analyses(
    client_id: str = "anonymous",
    _: None = Depends(check_limits)
):
    """Récupère la liste des analyses."""
    try:
        # TODO: Implement actual database query
        # For now returning mock data
        analyses = [
            {
                "id": "1",
                "user_id": client_id,
                "repositoryName": "example-repo",
                "status": "COMPLETED",
                "language": "python",
                "summary": "Analysis completed successfully",
                "metrics": {
                    "code_quality": 85,
                    "security_score": 90
                },
                "issues": [],
                "suggestions": [],
                "lines_of_code": 1000,
                "complexity_score": 75,
                "security_score": 85,
                "performance_score": 80,
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        return {"analyses": analyses}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analyses: {e}")
        raise HTTPException(500, str(e))

@app.get("/analysis/stats")
async def get_analysis_stats(
    client_id: str = "anonymous",
    _: None = Depends(check_limits)
):
    """Récupère les statistiques des analyses."""
    try:
        # TODO: Implement actual statistics calculation
        # For now returning mock data
        stats = {
            "data": {
                "totalScans": 150,
                "issuesFound": 45,
                "issuesResolved": 30,
                "averageResolutionTime": "2.5 days"
            }
        }
        return stats
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(500, str(e))

@app.post("/analyze")
@track_analysis("api")
async def analyze_code(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    client_id: str = "anonymous",
    _: None = Depends(check_limits)
):
    """
    Analyse du code source.
    
    Args:
        request: Requête contenant le code à analyser
        background_tasks: Tâches en arrière-plan
        client_id: ID du client
    """
    try:
        # Valider la requête
        if 'code' not in request:
            raise HTTPException(400, "Code manquant")
            
        # Ajouter à la file d'attente
        analysis_id = await analysis_queue.enqueue({
            'code': request['code'],
            'client_id': client_id,
            'options': request.get('options', {})
        })
        
        return {
            'analysis_id': analysis_id,
            'status': 'pending',
            'message': "Analyse en cours"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
        raise HTTPException(500, str(e))

@app.get("/status/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    client_id: str = "anonymous",
    _: None = Depends(check_limits)
):
    """Récupère le statut d'une analyse."""
    try:
        # TODO: Implémenter la récupération du statut
        return {
            'analysis_id': analysis_id,
            'status': 'pending'
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        raise HTTPException(500, str(e))

def start_api():
    """Démarre l'API."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_api()
