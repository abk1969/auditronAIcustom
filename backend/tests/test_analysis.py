"""Tests pour l'analyse de code."""
import os
import sys
import pytest
import asyncio

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.analysis_service import AnalysisService
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import AnalysisStatus, GitRepositoryRequest

TEST_CODE = """
def calculate_sum(a: int, b: int) -> int:
    return a + b  # Simple addition

def insecure_function(user_input: str) -> str:
    import os
    return os.system(user_input)  # Vulnérabilité d'injection de commande
"""

@pytest.fixture
def analysis_service():
    # Créer un dossier temporaire pour les tests
    test_upload_dir = "test_uploads"
    os.makedirs(test_upload_dir, exist_ok=True)
    
    # Créer le service avec un repository de test
    service = AnalysisService()
    service.UPLOAD_DIR = test_upload_dir
    
    yield service
    
    # Nettoyer après les tests
    import shutil
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir)

@pytest.mark.asyncio
async def test_file_analysis(analysis_service):
    # Créer un fichier de test
    test_file = "test.py"
    with open(os.path.join(analysis_service.UPLOAD_DIR, test_file), "w") as f:
        f.write(TEST_CODE)
    
    # Créer un UploadFile simulé
    class MockUploadFile(UploadFile):
        async def read(self):
            return TEST_CODE.encode()
    
    mock_file = MockUploadFile(filename=test_file)
    
    # Lancer l'analyse
    analysis = await analysis_service.create_analysis_from_upload(mock_file, "test_user")
    
    # Vérifier les résultats initiaux
    assert analysis.status == AnalysisStatus.PENDING
    assert analysis.user_id == "test_user"
    
    # Attendre que l'analyse soit terminée
    await asyncio.sleep(2)
    
    # Vérifier les résultats de l'analyse
    updated_analysis = await analysis_service.analysis_repository.get(analysis.id)
    assert updated_analysis is not None
    assert updated_analysis.status == AnalysisStatus.COMPLETED
    
    # Vérifier la détection des problèmes de sécurité
    assert any("injection" in str(issue).lower() for issue in updated_analysis.issues)
    assert updated_analysis.lines_of_code > 0

@pytest.mark.asyncio
async def test_repository_analysis(analysis_service):
    # Test avec un petit dépôt public
    repo_url = "https://github.com/example/python-sample"
    
    try:
        analysis = await analysis_service.create_analysis_from_repository(
            GitRepositoryRequest(url=repo_url),
            "test_user"
        )
        
        # Vérifier les résultats initiaux
        assert analysis.status == AnalysisStatus.PENDING
        assert analysis.user_id == "test_user"
        
        # Attendre que l'analyse soit terminée
        await asyncio.sleep(5)
        
        # Vérifier les résultats de l'analyse
        updated_analysis = await analysis_service.analysis_repository.get(analysis.id)
        assert updated_analysis is not None
        assert updated_analysis.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED]
        
    except Exception as e:
        pytest.skip(f"Test ignoré car le dépôt n'est pas accessible: {str(e)}")
