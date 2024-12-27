import streamlit as st
from pathlib import Path

def show_code_editor(default_code: str = "", language: str = "Python") -> str:
    """Affiche un éditeur de code avec coloration syntaxique."""
    return st.text_area(
        f"Code {language}",
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
    
    code_files = []
    for ext in [".py", ".ts", ".sql", ".txt", ".json", ".yaml", ".yml", ".md", ".css", ".html", ".js", ".jsx", ".tsx"]:
        code_files.extend(list(root_path.rglob(f"*{ext}")))
    
    if not code_files:
        st.sidebar.warning("Aucun fichier de code trouvé!")
        return None
    
    selected = st.sidebar.selectbox(
        "Fichiers de code",
        code_files,
        format_func=lambda x: x.name
    )
    
    return selected

def show_code_with_highlighting(code: str, filename: str = ""):
    """Affiche du code avec coloration syntaxique."""
    ext = Path(filename).suffix.lower()
    lang_map = {
        '.py': 'python',
        '.ts': 'typescript',
        '.sql': 'sql',
        '.txt': 'text',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.css': 'css',
        '.html': 'html',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.tsx': 'typescript'
    }
    language = lang_map.get(ext, 'text')
    st.code(code, language=language)

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
