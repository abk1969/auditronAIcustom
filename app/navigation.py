import streamlit as st
from pathlib import Path
from typing import Optional, List, Dict
from streamlit_option_menu import option_menu

def show_main_navigation():
    """Affiche le menu de navigation principal."""
    return option_menu(
        menu_title=None,
        options=[
            "Analyse de Code",
            "Statistiques",
            "Configuration"
        ],
        icons=[
            "code-square",
            "graph-up",
            "gear"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )

def show_stats_navigation():
    """Affiche le menu de navigation des statistiques."""
    return st.sidebar.radio(
        "Type de statistiques",
        options=[
            "Vue d'ensemble",
            "Analyse temporelle",
            "Comparaison des services",
            "Métriques de code",
            "Historique détaillé"
        ]
    )

def show_breadcrumb(items: List[str]):
    """Affiche un fil d'Ariane."""
    st.markdown(
        " > ".join(f"**{item}**" if i == len(items)-1 else item 
                  for i, item in enumerate(items))
    )

def show_recent_files():
    """Affiche les fichiers récemment analysés."""
    if 'recent_files' not in st.session_state:
        st.session_state.recent_files = []
    
    st.sidebar.markdown("### 📋 Fichiers récents")
    
    for file in st.session_state.recent_files[-5:]:  # Afficher les 5 derniers
        if st.sidebar.button(f"📄 {Path(file['path']).name}", key=file['path']):
            return file
    
    return None

def add_to_recent_files(file_path: str, stats: Dict):
    """Ajoute un fichier à l'historique."""
    if 'recent_files' not in st.session_state:
        st.session_state.recent_files = []
    
    # Éviter les doublons
    st.session_state.recent_files = [
        f for f in st.session_state.recent_files 
        if f['path'] != file_path
    ]
    
    st.session_state.recent_files.append({
        'path': file_path,
        'stats': stats,
        'timestamp': st.session_state.get('current_timestamp', '')
    })

def show_file_tree(root_path: Path) -> Optional[Path]:
    """Affiche une arborescence de fichiers interactive."""
    st.sidebar.markdown("### 📂 Explorateur")
    
    if not root_path.exists():
        st.sidebar.error("Dossier non trouvé!")
        return None
    
    def get_tree_data(path: Path, level: int = 0) -> List[Dict]:
        """Génère les données pour l'arborescence."""
        items = []
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                items.extend(get_tree_data(item, level + 1))
            elif item.suffix == '.py':
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'level': level,
                    'is_file': True
                })
        return items
    
    tree_data = get_tree_data(root_path)
    
    if not tree_data:
        st.sidebar.warning("Aucun fichier Python trouvé!")
        return None
    
    selected = None
    for item in tree_data:
        indent = "&nbsp;" * (4 * item['level'])
        icon = "📄" if item['is_file'] else "📁"
        if st.sidebar.button(
            f"{indent}{icon} {item['name']}", 
            key=item['path']
        ):
            selected = Path(item['path'])
    
    return selected 