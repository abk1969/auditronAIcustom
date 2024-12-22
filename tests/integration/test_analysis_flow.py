"""
Tests d'intégration pour le flux d'analyse
"""

import pytest
from pathlib import Path
from AuditronAI.core.security_analyzer import SecurityAnalyzer
from AuditronAI.core.custom_dataset import CustomDataset

@pytest.mark.integration
def test_full_analysis_flow(vulnerable_code):
    """Test du flux complet d'analyse."""
    # Initialisation des composants
    security_analyzer = SecurityAnalyzer()
    dataset = CustomDataset("integration_test")
    
    # Analyse de sécurité
    security_results = security_analyzer.analyze(vulnerable_code)
    assert 'summary' in security_results
    assert security_results['summary']['severity_counts']['high'] > 0
    
    # Analyse IA
    ai_results = dataset.generate_completion("project_analysis", {
        "file_path": "test.py",
        "code": vulnerable_code
    })
    assert isinstance(ai_results, str)
    assert len(ai_results) > 0 