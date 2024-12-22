import streamlit as st
from typing import Dict, Any
import json
from pathlib import Path

def load_user_config() -> Dict[str, Any]:
    """Charge la configuration utilisateur."""
    config_path = Path.home() / ".AuditronAI" / "config.json"
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user_config(config: Dict[str, Any]):
    """Sauvegarde la configuration utilisateur."""
    config_path = Path.home() / ".AuditronAI"
    config_path.mkdir(parents=True, exist_ok=True)
    
    with open(config_path / "config.json", 'w') as f:
        json.dump(config, f, indent=2)

def show_config_page():
    """Affiche la page de configuration."""
    st.markdown("## ⚙️ Configuration")
    
    config = load_user_config()
    
    # Thème
    theme = st.selectbox(
        "Thème",
        ["Light", "Dark", "Custom"],
        index=["Light", "Dark", "Custom"].index(
            config.get('theme', 'Light')
        )
    )
    
    # Taille maximale des fichiers
    max_size = st.number_input(
        "Taille maximale des fichiers (Ko)",
        value=config.get('max_file_size', 500) // 1024,
        min_value=1
    )
    
    # Patterns d'exclusion
    excluded = st.text_area(
        "Patterns à exclure (un par ligne)",
        value="\n".join(config.get('excluded_patterns', [
            'venv', '__pycache__', '*.pyc'
        ]))
    )
    
    # Options d'analyse
    st.markdown("### Options d'analyse")
    show_stats = st.checkbox(
        "Afficher les statistiques",
        value=config.get('show_stats', True)
    )
    show_code = st.checkbox(
        "Afficher le code source",
        value=config.get('show_code', True)
    )
    
    # Sauvegarder les changements
    if st.button("💾 Sauvegarder"):
        new_config = {
            'theme': theme,
            'max_file_size': max_size * 1024,
            'excluded_patterns': [
                p.strip() for p in excluded.split('\n') if p.strip()
            ],
            'show_stats': show_stats,
            'show_code': show_code
        }
        save_user_config(new_config)
        st.success("Configuration sauvegardée!")

def setup_page():
    """Configure la page Streamlit."""
    st.set_page_config(
        page_title="AuditronAI - Analyseur de Code Python",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/votre-repo/AuditronAI',
            'Report a bug': "https://github.com/votre-repo/AuditronAI/issues",
            'About': """
            # AuditronAI

            Analyseur de code Python avec IA et sécurité renforcée.
            
            ## Licences
            Ce projet utilise les composants open source suivants :
            - Streamlit (Apache License 2.0)
            - Bandit (Apache License 2.0)
            - Safety (MIT License)
            - Semgrep (LGPL-2.1 License)
            - Pylint (GPL-2.0 License)
            - Python-dotenv (BSD License)
            - Loguru (MIT License)
            
            ## Crédits
            - Interface utilisateur basée sur Streamlit
            - Analyse de sécurité : Bandit, Safety, Semgrep, Pylint
            - Logging : Loguru
            - Configuration : Python-dotenv
            
            ## Licence du projet
            Ce projet est distribué sous licence MIT.
            Copyright (c) 2024 AuditronAI
            """
        }
    )

def apply_theme(theme: str = "Light"):
    """Applique le thème choisi."""
    if theme == "Dark":
        st.markdown("""
            <style>
                .stApp { background-color: #0E1117; }
                .stButton > button { background-color: #262730; }
                .stTextInput > div > div > input { background-color: #262730; }
                .stats-card { background-color: #1E1E1E; color: white; }
                .navigation-menu { background-color: #262730; }
                .breadcrumb { background-color: #262730; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .stats-card { background-color: white; }
                .navigation-menu { background-color: #f8f9fa; }
                .breadcrumb { background-color: #f8f9fa; }
            </style>
        """, unsafe_allow_html=True)

def load_css():
    """Charge les styles CSS personnalisés."""
    st.markdown("""
        <style>
        /* Styles de base */
        .stApp {
            transition: background-color 0.3s ease;
        }
        
        /* Navigation */
        .navigation-menu {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            transition: background-color 0.3s ease;
        }
        
        /* Composants */
        .file-tree {
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.5;
        }
        
        .breadcrumb {
            padding: 0.5rem;
            border-radius: 3px;
            margin-bottom: 1rem;
            transition: background-color 0.3s ease;
        }
        
        .stats-card {
            padding: 1rem;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        /* Animations */
        .stButton > button {
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True) 