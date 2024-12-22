"""
AuditronAI.app
-------------
Interface utilisateur et composants Streamlit.
"""

__all__ = [
    'main',
    'show_analysis_page',
    'show_config_page',
    'show_code_editor',
    'show_file_browser'
]

from .components import show_code_editor, show_file_browser
from .pages import show_analysis_page, show_config_page

def main():
    """Point d'entrée de l'application."""
    from .streamlit_app import main as app_main
    return app_main() 