"""Configuration Sphinx pour la documentation automatique."""
from typing import Dict, Any
import os
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.ext.autodoc import between

# Configuration Sphinx
config = {
    'project': 'AuditronAI',
    'copyright': '2024, AuditronAI Team',
    'author': 'AuditronAI Team',
    'version': '1.0.0',
    'release': '1.0.0',
    'extensions': [
        'sphinx.ext.autodoc',
        'sphinx.ext.napoleon',
        'sphinx.ext.viewcode',
        'sphinx.ext.githubpages',
        'sphinx_rtd_theme'
    ],
    'templates_path': ['_templates'],
    'exclude_patterns': ['_build', 'Thumbs.db', '.DS_Store'],
    'html_theme': 'sphinx_rtd_theme',
    'html_static_path': ['_static']
}

def setup(app: Sphinx):
    """Configure Sphinx."""
    app.add_config_value('autodoc_member_order', 'bysource', True)
    app.connect('autodoc-process-docstring', between('^.*$', exclude=True)) 