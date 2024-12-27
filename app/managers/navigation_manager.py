"""
Manager class for handling navigation and menu components
"""

import streamlit as st
from typing import Callable, Dict, Any
from AuditronAI.core.logger import setup_logging

logger = setup_logging()

class NavigationManager:
    """Manages navigation and menu components of the application."""
    
    def __init__(self):
        """Initialize the navigation manager."""
        self.pages: Dict[str, Callable] = {}
        self.current_page: str = "Analyse"
    
    def add_page(self, name: str, page_func: Callable) -> None:
        """
        Add a page to the navigation.
        
        Args:
            name (str): Name of the page as shown in navigation
            page_func (Callable): Function to call when page is selected
        """
        self.pages[name] = page_func
    
    def show_navigation(self) -> str:
        """
        Display the navigation menu in the sidebar.
        
        Returns:
            str: Selected menu option
        """
        st.sidebar.title("🔍 Navigation")
        return st.sidebar.radio(
            label="Menu principal",
            options=list(self.pages.keys()),
            label_visibility="collapsed"
        )
    
    def show_welcome_message(self) -> None:
        """Display welcome message for first-time visitors."""
        if 'first_visit' not in st.session_state:
            st.session_state.first_visit = False
            st.balloons()
            st.success("""
                👋 Bienvenue sur AuditronAI !
                
                Cet outil vous aide à analyser votre code Python avec :
                - Analyse de sécurité avancée
                - Détection de vulnérabilités
                - Métriques de qualité
                - Recommandations d'amélioration
                
                Commencez en choisissant un mode d'analyse dans le menu de gauche.
            """)
    
    def render(self) -> None:
        """Render the current page based on navigation selection."""
        try:
            # Show welcome message if first visit
            self.show_welcome_message()
            
            # Get selected page from navigation
            selected = self.show_navigation()
            
            # Update current page
            self.current_page = selected
            
            # Render selected page
            if selected in self.pages:
                self.pages[selected]()
            else:
                logger.error(f"Page non trouvée : {selected}")
                st.error("Page non trouvée")
                
        except Exception as e:
            logger.error(f"Erreur de navigation : {str(e)}")
            st.error(f"Une erreur est survenue lors de la navigation : {str(e)}")
