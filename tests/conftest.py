"""
Fixtures partagées pour les tests
"""

import pytest
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configure l'environnement de test."""
    # Sauvegarder les variables d'environnement originales
    original_env = dict(os.environ)
    
    # Configurer l'environnement de test
    os.environ.update({
        'SECURITY_TIMEOUT': '5',
        'SECURITY_MAX_ISSUES': '50',
        'SECURITY_MIN_CONFIDENCE': '0.7',
        'MAX_FILE_SIZE': '10000'
    })
    
    yield
    
    # Restaurer l'environnement original
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def sample_code():
    """Retourne un exemple de code pour les tests."""
    return """
def add_numbers(a: int, b: int) -> int:
    \"\"\"Additionne deux nombres.\"\"\"
    return a + b

def multiply_numbers(a: int, b: int) -> int:
    \"\"\"Multiplie deux nombres.\"\"\"
    return a * b
"""

@pytest.fixture
def vulnerable_code():
    """Retourne un exemple de code vulnérable pour les tests."""
    return """
import os
import pickle

def execute_command(cmd: str):
    os.system(cmd)  # Injection de commande

def load_data(filename: str):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Désérialisation non sécurisée

PASSWORD = "admin123"  # Secret en dur
""" 