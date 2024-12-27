"""Package de tests pour les plugins AuditronAI."""

from pathlib import Path

# Chemins importants pour les tests de plugins
TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / 'fixtures'
PLUGINS_DIR = TEST_DIR / 'test_plugins'

# Créer les répertoires nécessaires
for dir_path in [FIXTURES_DIR, PLUGINS_DIR]:
    dir_path.mkdir(exist_ok=True) 