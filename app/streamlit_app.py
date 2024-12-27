"""
Point d'entrée de l'application Streamlit - Version refactorisée avec authentification
"""

import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from dotenv import load_dotenv
from AuditronAI.app.auth_ui import show_auth_page, is_authenticated, get_current_user, logout
from AuditronAI.app.config import setup_page, load_css, apply_theme
from AuditronAI.app.api_settings import show_api_settings
from AuditronAI.app.report_style import apply_report_style, show_analysis_report
from AuditronAI.app.stats_page import show_statistics_page
from AuditronAI.app.managers.analysis_ui_manager import AnalysisUIManager
from AuditronAI.app.managers.navigation_manager import NavigationManager
from AuditronAI.core.services.code_analyzer_service import CodeAnalyzerService
from AuditronAI.core.services.api_service import APIService
from AuditronAI.core.services.statistics_service import StatisticsService
from AuditronAI.core.logger import setup_logging

# Initialize core services
logger = setup_logging()
api_service = APIService()
stats_service = StatisticsService()
code_analyzer = CodeAnalyzerService()

# Initialize UI managers
ui_manager = AnalysisUIManager()
nav_manager = NavigationManager()

def show_analysis_page():
    """Affiche la page d'analyse de code."""
    st.title("🔍 Analyse de Code")
    
    # Get code input from UI
    code, filename = ui_manager.get_code_input()
    
    # Analysis options
    col1, col2 = st.columns(2)
    with col1:
        do_security = st.checkbox("Analyse de sécurité", value=True)
    with col2:
        do_ai = st.checkbox("Analyse par IA", value=False)
        
    if do_ai and not api_service.is_configured():
        st.warning("⚠️ Configuration API requise pour l'analyse IA")
        with st.expander("🔑 Configuration API"):
            show_api_settings()
    
    # Handle analysis
    if ui_manager.show_analysis_button():
        if code and code.strip():
            with st.spinner("Analyse en cours..."):
                try:
                    # Perform analysis
                    result = code_analyzer.analyze(
                        code=code,
                        filename=filename,
                        include_security=do_security,
                        include_ai=do_ai and api_service.is_configured()
                    )
                    
                    # Record statistics
                    stats_service.record_analysis(result)
                    
                    # Show report
                    show_analysis_report(result)
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {str(e)}")
                    logger.exception("Erreur d'analyse")
        else:
            st.warning("⚠️ Veuillez entrer du code à analyser")

def main():
    """Fonction principale de l'application."""
    try:
        # Setup application
        setup_page()
        load_css()
        apply_theme()
        apply_report_style()
        load_dotenv()

        # Vérifier l'authentification
        if not is_authenticated():
            show_auth_page()
            return

        # Afficher l'utilisateur connecté et le bouton de déconnexion
        user = get_current_user()
        if not user:
            # Si l'utilisateur n'est pas valide, le déconnecter
            logout()
            return

        with st.sidebar:
            st.write(f"👤 Connecté en tant que : {user['first_name']} {user['last_name']}")
            if st.button("🚪 Déconnexion"):
                logout()
                st.rerun()
        
        # Configure navigation
        nav_manager.add_page("Analyse", show_analysis_page)
        nav_manager.add_page("Statistiques", lambda: show_statistics_page(
            stats_service.history,
            stats_service.usage_stats
        ))
        
        # Render application
        nav_manager.render()

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
        logger.error(f"Erreur dans l'application : {str(e)}")

if __name__ == "__main__":
    main()
