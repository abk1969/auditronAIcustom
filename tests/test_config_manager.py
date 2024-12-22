"""
Tests pour le gestionnaire de configuration
"""

import pytest
from pathlib import Path
from AuditronAI.core.config_manager import ConfigManager

@pytest.fixture
def config_manager():
    """Fixture pour le gestionnaire de configuration."""
    return ConfigManager()

def test_default_values(config_manager):
    """Test des valeurs par défaut."""
    config = config_manager.get_config()
    assert config['ai']['service'] in ['openai', 'google']
    assert isinstance(config['security']['timeout'], int)
    assert isinstance(config['security']['max_issues'], int)
    assert isinstance(config['security']['min_confidence'], float)

def test_update_config(config_manager):
    """Test de la mise à jour de la configuration."""
    updates = {
        'SECURITY_TIMEOUT': '60',
        'SECURITY_MAX_ISSUES': '200'
    }
    config_manager.update_config(updates)
    config = config_manager.get_config()
    assert config['security']['timeout'] == 60
    assert config['security']['max_issues'] == 200

def test_invalid_updates(config_manager):
    """Test des mises à jour invalides."""
    with pytest.raises(ValueError):
        config_manager.update_config({
            'SECURITY_TIMEOUT': 'invalid'
        }) 