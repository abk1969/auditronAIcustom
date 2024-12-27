"""Tests pour le plugin d'analyse de complexité."""
import pytest
from pathlib import Path
from AuditronAI.core.plugins.manager import PluginManager
from AuditronAI.core.plugins.base import PluginType
from .fixtures.test_code_samples import COMPLEX_CODE, TEST_FILE_CODE, INVALID_CODE

@pytest.fixture
def plugin_manager():
    """Fixture pour le gestionnaire de plugins."""
    manager = PluginManager(plugins_dir=Path(__file__).parent.parent.parent / "plugins")
    manager.discover_plugins()
    return manager

@pytest.fixture
def complexity_plugin(plugin_manager):
    """Fixture pour le plugin de complexité."""
    plugin = plugin_manager.initialize_plugin("complexity_analyzer")
    assert plugin is not None
    return plugin

def test_complexity_analyzer_loading(plugin_manager):
    """Test le chargement du plugin."""
    plugins = plugin_manager.get_plugins_by_type(PluginType.ANALYZER)
    assert any(p.name == "complexity_analyzer" for p in plugins)

def test_complex_code_analysis(plugin_manager):
    """Test l'analyse de code complexe."""
    result = plugin_manager.execute_plugin("complexity_analyzer", COMPLEX_CODE)
    
    assert result is not None
    assert result['complexity_score'] > 10  # Code très complexe
    assert len(result['details']) == 2  # Deux fonctions
    
    # Vérifier la fonction complexe
    complex_func = next(d for d in result['details'] if d['name'] == 'very_complex_function')
    assert complex_func['complexity'] > 5

def test_test_file_ignored(plugin_manager):
    """Test que les fichiers de test sont ignorés."""
    result = plugin_manager.execute_plugin("complexity_analyzer", TEST_FILE_CODE)
    assert result['complexity_score'] == 0  # Ignoré car fichier de test

def test_invalid_code_handling(plugin_manager):
    """Test la gestion du code invalide."""
    result = plugin_manager.execute_plugin("complexity_analyzer", INVALID_CODE)
    assert 'error' in result

def test_threshold_warnings(complexity_plugin):
    """Test les avertissements de seuil."""
    config = complexity_plugin._config['settings']
    assert config['max_complexity'] == 10
    
    result = plugin_manager.execute_plugin("complexity_analyzer", COMPLEX_CODE)
    assert result['complexity_score'] > config['max_complexity']

@pytest.mark.parametrize("code,expected_score", [
    ("def simple(): return 42", 1),
    ("def empty(): pass", 1),
    (COMPLEX_CODE, 15),  # Valeur approximative
])
def test_complexity_scores(plugin_manager, code, expected_score):
    """Test différents scores de complexité."""
    result = plugin_manager.execute_plugin("complexity_analyzer", code)
    assert abs(result['complexity_score'] - expected_score) <= 2  # Marge d'erreur 