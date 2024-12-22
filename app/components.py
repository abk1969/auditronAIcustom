import streamlit as st
from pathlib import Path

def show_code_editor(default_code: str = "") -> str:
    """Affiche un éditeur de code avec coloration syntaxique."""
    return st.text_area(
        "Code Python",
        value=default_code,
        height=300,
        key="code_editor"
    )

def show_file_browser():
    """Affiche un explorateur de fichiers."""
    st.sidebar.markdown("### 📂 Explorateur")
    root_path = Path(".")
    
    if not root_path.exists():
        st.sidebar.error("❌ Dossier non trouvé!")
        return None
    
    python_files = list(root_path.rglob("*.py"))
    if not python_files:
        st.sidebar.warning("Aucun fichier Python trouvé!")
        return None
    
    selected = st.sidebar.selectbox(
        "Fichiers Python",
        python_files,
        format_func=lambda x: x.name
    )
    
    return selected

def show_code_with_highlighting(code: str):
    """Affiche du code avec coloration syntaxique."""
    st.code(code, language="python")

def show_active_service():
    """Affiche le service AI actif."""
    service = st.session_state.get('current_service', 'openai')
    st.markdown(f"**Service actif:** {service.upper()}")

def add_service_indicator_css():
    """Ajoute le CSS pour l'indicateur de service."""
    st.markdown("""
        <style>
        .service-indicator {
            padding: 5px 10px;
            border-radius: 5px;
            background: #2E2E2E;
            color: white;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)