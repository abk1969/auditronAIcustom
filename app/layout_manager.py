import streamlit as st

def init_layout_state():
    """Initialise l'état du layout."""
    if 'layout' not in st.session_state:
        st.session_state.layout = {
            'show_params': True,
            'show_code': True,
            'show_analysis': True
        }

def toggle_section(section_name: str):
    """Bascule la visibilité d'une section."""
    st.session_state.layout[f'show_{section_name}'] = not st.session_state.layout[f'show_{section_name}']

def show_layout_controls():
    """Affiche les contrôles de layout."""
    st.markdown("""
        <div style='background: #2E2E2E; padding: 10px; border-radius: 8px; margin-bottom: 20px;
                  display: flex; gap: 10px; justify-content: flex-end;'>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    
    with col1:
        if st.button(
            "⚙️ Paramètres" if st.session_state.layout['show_params'] else "⚙️ ~~Paramètres~~",
            help="Afficher/Masquer les paramètres",
            use_container_width=True
        ):
            toggle_section('params')
    
    with col2:
        if st.button(
            "📝 Code" if st.session_state.layout['show_code'] else "📝 ~~Code~~",
            help="Afficher/Masquer le code",
            use_container_width=True
        ):
            toggle_section('code')
    
    with col3:
        if st.button(
            "📊 Analyse" if st.session_state.layout['show_analysis'] else "📊 ~~Analyse~~",
            help="Afficher/Masquer l'analyse",
            use_container_width=True
        ):
            toggle_section('analysis')
    
    st.markdown("</div>", unsafe_allow_html=True) 