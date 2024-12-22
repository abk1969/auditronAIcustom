import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path
import os

def show_project_explorer():
    """Affiche un explorateur de projet avancé."""
    st.sidebar.markdown("### 📂 Explorateur de projet")
    
    # Sélection du dossier racine
    root_path = st.sidebar.text_input("Dossier racine", ".")
    root_path = Path(root_path).resolve()
    
    if not root_path.exists():
        st.sidebar.error("❌ Dossier non trouvé!")
        return None
    
    # Filtres
    with st.sidebar.expander("🔍 Filtres", expanded=False):
        show_hidden = st.checkbox("Afficher les fichiers cachés", False)
        file_types = st.multiselect(
            "Types de fichiers",
            [".py", ".ipynb", ".txt", ".md"],
            default=[".py"]
        )
        size_limit = st.slider(
            "Taille max (Ko)",
            0, 1000, 500
        )
    
    # Organisation
    sort_by = st.sidebar.selectbox(
        "Trier par",
        ["Nom", "Date", "Taille", "Type"]
    )
    
    # Vue en arbre ou liste
    view_mode = st.sidebar.radio(
        "Mode d'affichage",
        ["Arbre", "Liste"]
    )
    
    return {
        "root": root_path,
        "filters": {
            "show_hidden": show_hidden,
            "types": file_types,
            "size_limit": size_limit * 1024
        },
        "sort_by": sort_by,
        "view_mode": view_mode
    }

def show_breadcrumbs(path: Path, root: Path):
    """Affiche un fil d'Ariane cliquable."""
    parts = path.relative_to(root).parts
    breadcrumbs = []
    current = root
    
    for part in parts:
        current = current / part
        if st.button(part, key=f"breadcrumb_{part}"):
            return current
    
    return path

def show_file_actions(file_path: Path):
    """Affiche les actions disponibles pour un fichier."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Analyser", key=f"analyze_{file_path}"):
            return "analyze"
    
    with col2:
        if st.button("📝 Éditer", key=f"edit_{file_path}"):
            return "edit"
    
    with col3:
        if st.button("📊 Historique", key=f"history_{file_path}"):
            return "history"
    
    return None

def show_quick_actions():
    """Affiche une barre d'actions rapides."""
    st.markdown("""
        <div class="quick-actions">
            <div class="action-group">
                <button>📄 Nouveau fichier</button>
                <button>📁 Nouveau dossier</button>
                <button>📋 Coller</button>
            </div>
            <div class="action-group">
                <button>🔄 Actualiser</button>
                <button>⚙️ Paramètres</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_file_preview(file_path: Path):
    """Affiche un aperçu du fichier."""
    if not file_path.exists():
        return
    
    with st.expander("👁️ Aperçu", expanded=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Limiter l'aperçu à 1000 caractères
            if len(content) > 1000:
                content = content[:1000] + "\n..."
            
            st.code(content, language="python")
        except Exception as e:
            st.error(f"Erreur lors de la lecture : {str(e)}")

def show_file_info(file_path: Path):
    """Affiche les informations sur le fichier."""
    if not file_path.exists():
        return
    
    stats = file_path.stat()
    
    st.markdown(f"""
        <div class="file-info">
            <div class="info-item">
                <span class="label">Taille:</span>
                <span class="value">{stats.st_size / 1024:.1f} Ko</span>
            </div>
            <div class="info-item">
                <span class="label">Modifié:</span>
                <span class="value">{stats.st_mtime}</span>
            </div>
            <div class="info-item">
                <span class="label">Type:</span>
                <span class="value">{file_path.suffix}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def apply_navigation_style():
    """Applique le style pour la navigation."""
    st.markdown("""
        <style>
        .quick-actions {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .action-group {
            display: flex;
            gap: 10px;
        }
        
        .action-group button {
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            background: #e9ecef;
            cursor: pointer;
        }
        
        .action-group button:hover {
            background: #dee2e6;
        }
        
        .file-info {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .info-item .label {
            color: #666;
            font-weight: 500;
        }
        
        .breadcrumb {
            display: flex;
            gap: 5px;
            align-items: center;
            padding: 5px 10px;
            background: #f8f9fa;
            border-radius: 3px;
            margin-bottom: 10px;
        }
        
        .breadcrumb-item {
            cursor: pointer;
            padding: 2px 5px;
            border-radius: 3px;
        }
        
        .breadcrumb-item:hover {
            background: #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True) 