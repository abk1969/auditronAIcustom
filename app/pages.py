import streamlit as st
from pathlib import Path
from .components import show_code_editor, show_file_browser, show_code_with_highlighting
from .report_style import show_analysis_report
from .api_settings import show_api_settings
from AuditronAI.core.analyzer import analyze_code
from AuditronAI.core.logger import logger
import os
from dotenv import load_dotenv, set_key

def init_page_state():
    """Initialise l'état de la page."""
    # États de base
    if 'page' not in st.session_state:
        st.session_state.page = 'analyse'
    if 'analysis_step' not in st.session_state:
        st.session_state.analysis_step = 1
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = "Fichier unique"
    
    # État de l'analyse
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    
    # État de la configuration
    if 'security_config' not in st.session_state:
        st.session_state.security_config = {
            'critical_threshold': int(os.getenv('CRITICAL_SEVERITY_THRESHOLD', 0)),
            'high_threshold': int(os.getenv('HIGH_SEVERITY_THRESHOLD', 2)),
            'medium_threshold': int(os.getenv('MEDIUM_SEVERITY_THRESHOLD', 5))
        }

def check_api_configuration():
    """Vérifie si les API sont configurées."""
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.warning("⚠️ Aucune clé API configurée. Veuillez configurer une API avant de continuer.")
        with st.expander("🔑 Configuration API", expanded=True):
            show_api_settings()
        return False
    return True

def save_security_config(config: dict):
    """Sauvegarde la configuration de sécurité dans .env."""
    env_path = Path(".env")
    
    # Charger les variables existantes
    load_dotenv(env_path)
    
    # Mettre à jour les seuils
    set_key(env_path, "CRITICAL_SEVERITY_THRESHOLD", str(config['critical_threshold']))
    set_key(env_path, "HIGH_SEVERITY_THRESHOLD", str(config['high_threshold']))
    set_key(env_path, "MEDIUM_SEVERITY_THRESHOLD", str(config['medium_threshold']))
    
    # Recharger les variables
    load_dotenv(override=True)

def reset_security_config():
    """Réinitialise les seuils de sécurité aux valeurs par défaut."""
    default_config = {
        'critical_threshold': 0,  # Aucune vulnérabilité critique tolérée
        'high_threshold': 2,      # Maximum 2 vulnérabilités importantes
        'medium_threshold': 5     # Maximum 5 vulnérabilités moyennes
    }
    
    try:
        save_security_config(default_config)
        st.session_state.security_config = default_config
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation: {str(e)}")
        return False

def show_analysis_page():
    """Affiche la page d'analyse de code."""
    init_page_state()
    
    try:
        # Vérifier la configuration API
        if not check_api_configuration():
            st.warning("⚠️ Configuration API requise")
            show_api_settings()
            return
        
        # Étape 1: Choix du mode
        st.markdown("### Étape 1: Choisir le mode d'analyse")
        st.session_state.analysis_mode = st.radio(
            "Mode d'analyse",
            ["Fichier unique", "Dossier complet", "Éditeur de code"],
            horizontal=True,
            index=["Fichier unique", "Dossier complet", "Éditeur de code"].index(st.session_state.analysis_mode)
        )
        
        # Zone de code
        st.markdown("### Étape 2: Code source")
        code = None
        filename = None
        
        if st.session_state.analysis_mode == "Fichier unique":
            uploaded_file = st.file_uploader(
                "Sélectionnez un fichier Python",
                type=['py'],
                key='file_uploader'
            )
            if uploaded_file:
                code = uploaded_file.getvalue().decode()
                filename = uploaded_file.name
                if st.checkbox("Voir le code", value=False):
                    st.code(code, language="python")
                st.session_state.analysis_step = 2
                
        elif st.session_state.analysis_mode == "Dossier complet":
            selected_file = show_file_browser()
            if selected_file and selected_file.exists():
                with open(selected_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                filename = str(selected_file)
                if st.checkbox("Voir le code", value=False):
                    st.code(code, language="python")
                st.session_state.analysis_step = 2
                
        else:  # Éditeur de code
            code = show_code_editor()
            if code and code.strip():
                filename = "editeur.py"
                st.session_state.analysis_step = 2
        
        # Bouton d'analyse
        if code:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Lancer l'analyse", use_container_width=True):
                    with st.spinner("Analyse en cours..."):
                        try:
                            result = analyze_code(code, filename)
                            st.session_state.last_analysis = result
                            st.session_state.analysis_step = 3
                        except Exception as e:
                            st.error(f"Erreur lors de l'analyse: {str(e)}")
        
        # Affichage des résultats
        if st.session_state.analysis_step == 3 and 'last_analysis' in st.session_state:
            result = st.session_state.last_analysis
            if 'error' in result:
                st.error(f"Erreur lors de l'analyse : {result['error']}")
            show_analysis_report(result)
            
            # Bouton nouvelle analyse
            if st.button("🔄 Nouvelle analyse"):
                st.session_state.analysis_step = 1
                st.experimental_rerun()
        
    except Exception as e:
        logger.error(f"Erreur dans l'interface: {str(e)}")
        st.error("Une erreur est survenue. Veuillez réessayer.")
        if os.getenv('DEBUG', 'false').lower() == 'true':
            st.exception(e)
    
    # Indicateur de progression
    progress_text = {
        1: "📝 Sélection du code",
        2: "🔍 Code chargé, prêt pour l'analyse",
        3: "✅ Analyse terminée"
    }
    
    st.sidebar.markdown("### Progression")
    st.sidebar.markdown(progress_text.get(st.session_state.analysis_step, ""))
    
    with st.sidebar.expander("ℹ️ Aide", expanded=False):
        st.markdown("""
            ### Comment utiliser l'analyseur
            1. Choisissez un mode d'analyse
            2. Chargez ou saisissez votre code
            3. Lancez l'analyse
            4. Consultez les résultats
            
            ### Modes disponibles
            - **Fichier unique**: Analysez un fichier .py
            - **Dossier complet**: Parcourez vos fichiers
            - **Éditeur de code**: Saisissez du code directement
        """)

def show_config_page():
    """Affiche la page de configuration."""
    st.markdown("## ⚙️ Configuration")
    
    # Configuration API
    with st.expander("🔑 Configuration API", expanded=True):
        show_api_settings()
    
    # Configuration sécurité
    with st.expander("🛡️ Configuration de sécurité", expanded=True):
        st.markdown("### Seuils de sévérité")
        
        # Boutons d'action
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Réinitialiser", help="Revenir aux valeurs par défaut"):
                if reset_security_config():
                    st.success("Configuration réinitialisée!")
                else:
                    st.error("Erreur lors de la réinitialisation")
        
        # Sauvegarder les valeurs dans session_state
        if 'security_config' not in st.session_state:
            st.session_state.security_config = {
                'critical_threshold': int(os.getenv('CRITICAL_SEVERITY_THRESHOLD', 0)),
                'high_threshold': int(os.getenv('HIGH_SEVERITY_THRESHOLD', 2)),
                'medium_threshold': int(os.getenv('MEDIUM_SEVERITY_THRESHOLD', 5))
            }
        
        # Interface de configuration
        config_changed = False
        
        new_critical = st.slider(
            "Seuil critique", 0, 5, 
            st.session_state.security_config['critical_threshold'],
            help="Nombre maximum de vulnérabilités critiques acceptées"
        )
        if new_critical != st.session_state.security_config['critical_threshold']:
            st.session_state.security_config['critical_threshold'] = new_critical
            config_changed = True
        
        new_high = st.slider(
            "Seuil élevé", 0, 10, 
            st.session_state.security_config['high_threshold'],
            help="Nombre maximum de vulnérabilités importantes acceptées"
        )
        if new_high != st.session_state.security_config['high_threshold']:
            st.session_state.security_config['high_threshold'] = new_high
            config_changed = True
        
        new_medium = st.slider(
            "Seuil moyen", 0, 15, 
            st.session_state.security_config['medium_threshold'],
            help="Nombre maximum de vulnérabilités moyennes acceptées"
        )
        if new_medium != st.session_state.security_config['medium_threshold']:
            st.session_state.security_config['medium_threshold'] = new_medium
            config_changed = True
        
        # Sauvegarder si changements
        if config_changed:
            if st.button("💾 Sauvegarder la configuration"):
                try:
                    save_security_config(st.session_state.security_config)
                    st.success("Configuration sauvegardée!")
                except Exception as e:
                    st.error(f"Erreur lors de la sauvegarde: {str(e)}")