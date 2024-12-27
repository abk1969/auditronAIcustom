"""
Manager class for handling analysis UI components and interactions
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Tuple
from AuditronAI.app.components import show_code_editor, show_file_browser
from AuditronAI.core.logger import setup_logging

logger = setup_logging()

class AnalysisUIManager:
    """Manages the UI components for code analysis."""
    
    @staticmethod
    def show_analysis_mode_selector() -> str:
        """Display and handle the analysis mode selection.
        
        Returns:
            str: Selected analysis mode
        """
        return st.radio(
            label="Mode d'analyse",
            options=["Fichier", "Éditeur", "Dossier"],
            horizontal=True
        )
    
    def handle_file_upload(self) -> Tuple[Optional[str], Optional[str]]:
        """Handle file upload mode UI and logic.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Tuple of (code, filename) if successful
        """
        st.markdown("Types de fichiers acceptés: .py, .ts, .sql, .txt, .json, .yaml, .yml, .md, .css, .html, .js, .jsx, .tsx")
        uploaded_file = st.file_uploader(
            "Choisir un fichier à analyser",
            type=['py', 'ts', 'sql', 'txt', 'json', 'yaml', 'yml', 'md', 'css', 'html', 'js', 'jsx', 'tsx'],
            accept_multiple_files=False
        )
        if uploaded_file:
            try:
                # Handle the file content
                content = uploaded_file.getvalue()
                
                # For TypeScript files, ensure proper handling
                if uploaded_file.name.endswith(('.ts', '.tsx')):
                    uploaded_file.type = 'application/typescript'
                
                code = content.decode('utf-8')
                filename = uploaded_file.name
                if st.checkbox("Voir le code"):
                    # Déterminer le langage en fonction de l'extension
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
                return code, filename
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
                logger.error(f"Erreur de lecture : {str(e)}")
        return None, None
    
    def handle_folder_selection(self) -> Tuple[Optional[str], Optional[str]]:
        """Handle folder selection mode UI and logic.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Tuple of (code, filename) if successful
        """
        selected_file = show_file_browser()
        if selected_file and selected_file.exists():
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                filename = str(selected_file)
                if st.checkbox("Voir le code"):
                    # Déterminer le langage en fonction de l'extension
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
                return code, filename
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {str(e)}")
                logger.error(f"Erreur de lecture : {str(e)}")
        return None, None
    
    def handle_editor_mode(self) -> Tuple[Optional[str], Optional[str]]:
        """Handle editor mode UI and logic.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Tuple of (code, filename) if successful
        """
        file_type = st.selectbox(
            "Type de fichier",
            options=[
                "Python (.py)", 
                "TypeScript (.ts)", 
                "SQL (.sql)",
                "Text (.txt)",
                "JSON (.json)",
                "YAML (.yaml)",
                "Markdown (.md)",
                "CSS (.css)",
                "HTML (.html)",
                "JavaScript (.js)",
                "React (.jsx)",
                "TypeScript React (.tsx)"
            ]
        )
        
        ext_map = {
            "Python (.py)": ".py",
            "TypeScript (.ts)": ".ts",
            "SQL (.sql)": ".sql",
            "Text (.txt)": ".txt",
            "JSON (.json)": ".json",
            "YAML (.yaml)": ".yaml",
            "Markdown (.md)": ".md",
            "CSS (.css)": ".css",
            "HTML (.html)": ".html",
            "JavaScript (.js)": ".js",
            "React (.jsx)": ".jsx",
            "TypeScript React (.tsx)": ".tsx"
        }
        
        # Map des types de fichiers vers les langages pour la coloration syntaxique
        lang_map = {
            "Python (.py)": "python",
            "TypeScript (.ts)": "typescript",
            "SQL (.sql)": "sql",
            "Text (.txt)": "text",
            "JSON (.json)": "json",
            "YAML (.yaml)": "yaml",
            "Markdown (.md)": "markdown",
            "CSS (.css)": "css",
            "HTML (.html)": "html",
            "JavaScript (.js)": "javascript",
            "React (.jsx)": "javascript",
            "TypeScript React (.tsx)": "typescript"
        }
        language = lang_map[file_type]
        code = show_code_editor(language=language)
        if code:
            ext = ext_map[file_type]
            return code, f"editor_code{ext}"
        return None, None
    
    def get_code_input(self) -> Tuple[Optional[str], Optional[str]]:
        """Get code input based on selected mode.
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Tuple of (code, filename) if successful
        """
        mode = self.show_analysis_mode_selector()
        
        if mode == "Fichier":
            return self.handle_file_upload()
        elif mode == "Dossier":
            return self.handle_folder_selection()
        else:  # Editor mode
            return self.handle_editor_mode()
    
    def show_analysis_button(self) -> bool:
        """Display the analysis button.
        
        Returns:
            bool: True if button was clicked
        """
        return st.button("🚀 Analyser le code", use_container_width=True)
