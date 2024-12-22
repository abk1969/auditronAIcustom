"""
Tests pour le module security_analyzer
"""

import pytest
from pathlib import Path
from AuditronAI.core.security_analyzer import SecurityAnalyzer

@pytest.fixture
def analyzer():
    """Fixture pour l'analyseur de sécurité."""
    return SecurityAnalyzer()

def test_validate_thresholds():
    """Test de la validation des seuils."""
    analyzer = SecurityAnalyzer()
    
    # Test des seuils valides
    analyzer.thresholds = {'critical': 0, 'high': 2, 'medium': 5}
    assert analyzer.validate_thresholds() is True
    
    # Test des seuils invalides
    analyzer.thresholds = {'critical': 3, 'high': 2, 'medium': 5}
    assert analyzer.validate_thresholds() is False

def test_analyze_empty_code(analyzer):
    """Test de l'analyse de code vide."""
    result = analyzer.analyze("")
    assert 'error' in result
    assert result['error'] == "Le code à analyser est vide"

def test_analyze_valid_code(analyzer):
    """Test de l'analyse de code valide."""
    code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    result = analyzer.analyze(code)
    assert 'error' not in result
    assert 'summary' in result
    assert 'severity_counts' in result['summary'] 

def test_analyze_large_file(analyzer):
    """Test de l'analyse d'un fichier trop volumineux."""
    # Créer un grand fichier
    large_code = "x = 1\n" * 100000
    result = analyzer.analyze(large_code)
    assert 'error' in result
    assert "Fichier trop volumineux" in result['error']

def test_analyze_security_issues(analyzer):
    """Test de la détection des problèmes de sécurité."""
    code = """
import os
def execute_command(cmd):
    os.system(cmd)  # Vulnérabilité d'injection de commande
    """
    result = analyzer.analyze(code)
    assert result['security']['summary']['severity_counts']['high'] > 0

def test_timeout(analyzer):
    """Test du timeout de l'analyse."""
    # Simuler un long code
    code = """
def factorial(n):
    if n == 0: return 1
    return n * factorial(n-1)
result = factorial(1000)
"""
    result = analyzer.analyze(code)
    assert 'error' not in result or "délai" in result['error']

def test_run_bandit_analysis(analyzer):
    """Test de l'analyse Bandit."""
    code = """
import pickle
def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Vulnérabilité désérialisation
    """
    result = analyzer.run_bandit_analysis(code, "test.py")
    assert 'issues' in result
    assert len(result['issues']) > 0

def test_run_safety_check(analyzer):
    """Test de la vérification des dépendances."""
    result = analyzer.run_safety_check()
    assert isinstance(result, dict)
    assert 'issues' in result

def test_run_semgrep_analysis(analyzer):
    """Test de l'analyse Semgrep."""
    code = """
def login(username, password):
    if username == 'admin' and password == 'admin':  # Mot de passe en dur
        return True
    """
    result = analyzer.run_semgrep_analysis(code)
    assert isinstance(result, dict)
    assert 'issues' in result

@pytest.mark.parametrize("threshold_config", [
    {'critical': 0, 'high': 2, 'medium': 5},  # Valide
    {'critical': -1, 'high': 2, 'medium': 5},  # Invalide (négatif)
    {'critical': 3, 'high': 2, 'medium': 5},  # Invalide (ordre)
])
def test_threshold_validation(analyzer, threshold_config):
    """Test des différentes configurations de seuils."""
    analyzer.thresholds = threshold_config
    is_valid = analyzer.validate_thresholds()
    
    if threshold_config['critical'] < 0:
        assert not is_valid, "Les seuils négatifs devraient être invalides"
    elif threshold_config['critical'] > threshold_config['high']:
        assert not is_valid, "Le seuil critique ne peut pas être supérieur au seuil élevé"
    else:
        assert is_valid, "La configuration valide devrait être acceptée"