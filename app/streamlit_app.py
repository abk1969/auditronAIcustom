"""
Point d'entrée de l'application Streamlit
"""

import streamlit as st
from pathlib import Path
import os
from dotenv import load_dotenv
from AuditronAI.app.config import setup_page, load_css, apply_theme
from AuditronAI.app.components import show_code_editor, show_file_browser
from AuditronAI.app.api_settings import show_api_settings
from AuditronAI.app.report_style import apply_report_style, show_analysis_report
from AuditronAI.app.stats_page import show_statistics_page
from AuditronAI.core.logger import setup_logger
from AuditronAI.core.history import AnalysisHistory
from AuditronAI.core.usage_stats import UsageStats
from AuditronAI.core import SecurityAnalyzer
from AuditronAI.core.custom_dataset import CustomDataset

# Initialiser le logger
logger = setup_logger()

def analyze_code(code: str, filename: str = "code.py") -> dict:
    """Analyse un code Python donné."""
    try:
        # Analyse IA
        dataset = CustomDataset("streamlit_analysis")
        ai_result = dataset.generate_completion("project_analysis", {
            "code": code,
            "file_path": filename
        })
        
        # Analyse de sécurité
        security_analyzer = SecurityAnalyzer()
        security_results = security_analyzer.analyze(code, filename)
        
        # Statistiques de base
        lines = code.split('\n')
        stats = {
            'Lignes de code': len(lines),
            'Caractères': len(code),
            'Fonctions': len([l for l in lines if l.strip().startswith('def ')]),
            'Classes': len([l for l in lines if l.strip().startswith('class ')])
        }
        
        return {
            "file": filename,
            "code": code,
            "analysis": ai_result,
            "stats": stats,
            "security": security_results
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        raise

def main():
    """Fonction principale de l'application."""
    try:
        setup_page()
        load_css()
        apply_theme()
        apply_report_style()
        
        history = AnalysisHistory()
        usage_stats = UsageStats()

        # Menu principal
        st.sidebar.title("🔍 Navigation")
        menu = st.sidebar.radio(
            label="Menu principal",
            options=["Analyse", "Statistiques", "Configuration"],
            label_visibility="collapsed"
        )

        if menu == "Analyse":
            st.title("🔍 Analyse de Code")
            
            # Configuration API
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                st.error("⚠️ Configuration API requise")
                with st.expander("🔑 Configuration API", expanded=True):
                    show_api_settings()
                return
            
            # Mode d'analyse
            mode = st.radio(
                label="Mode d'analyse",
                options=["Fichier", "Éditeur", "Dossier"],
                horizontal=True
            )
            
            code = None
            filename = "code.py"
            
            if mode == "Fichier":
                uploaded_file = st.file_uploader("Choisir un fichier Python", type=['py'])
                if uploaded_file:
                    try:
                        code = uploaded_file.getvalue().decode('utf-8')
                        filename = uploaded_file.name
                        if st.checkbox("Voir le code"):
                            st.code(code, language='python')
                    except Exception as e:
                        st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
                        logger.error(f"Erreur de lecture : {str(e)}")
                        code = None
            elif mode == "Dossier":
                selected_file = show_file_browser()
                if selected_file and selected_file.exists():
                    try:
                        with open(selected_file, 'r', encoding='utf-8') as f:
                            code = f.read()
                        filename = str(selected_file)
                        if st.checkbox("Voir le code"):
                            st.code(code, language='python')
                    except Exception as e:
                        st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
                        logger.error(f"Erreur de lecture : {str(e)}")
                        code = None
            else:
                code = show_code_editor()
                if code:
                    filename = "editor_code.py"

            # Bouton d'analyse
            if st.button("🚀 Analyser le code", use_container_width=True):
                if code and code.strip():
                    with st.spinner("Analyse en cours..."):
                        try:
                            result = analyze_code(code, filename)
                            
                            # Enregistrer dans l'historique
                            history.add_entry(result)
                            usage_stats.record_analysis(os.getenv('AI_SERVICE', 'openai'))
                            
                            # Afficher les résultats
                            show_analysis_report(result)
                            
                        except Exception as e:
                            st.error(f"Erreur lors de l'analyse : {str(e)}")
                            logger.error(f"Erreur d'analyse : {str(e)}")
                else:
                    st.warning("⚠️ Veuillez entrer du code à analyser")

        elif menu == "Statistiques":
            show_statistics_page(history, usage_stats)
        else:
            show_api_settings()

    except Exception as e:
        st.error(f"Une erreur est survenue : {str(e)}")
        logger.error(f"Erreur dans l'application : {str(e)}")

if __name__ == "__main__":
    main() 