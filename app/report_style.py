"""Module pour le style des rapports d'analyse."""
import streamlit as st
from AuditronAI.app.components import show_code_with_highlighting
from pathlib import Path
from AuditronAI.app.visualizations import (
    show_code_metrics,
    show_code_complexity_chart,
    show_quality_indicators,
    show_code_issues,
    show_code_coverage
)

def show_issues_summary(result: dict):
    """Affiche le résumé des problèmes style SonarQube."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="issue-box bug">
                <div class="issue-icon">🐛</div>
                <div class="issue-count">0</div>
                <div class="issue-label">Bugs</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="issue-box security">
                <div class="issue-icon">🔒</div>
                <div class="issue-count">0</div>
                <div class="issue-label">Vulnérabilités</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="issue-box smell">
                <div class="issue-icon">🔍</div>
                <div class="issue-count">0</div>
                <div class="issue-label">Code Smells</div>
            </div>
        """, unsafe_allow_html=True)

def apply_report_style():
    """Applique le style inspiré de SonarQube et Google Gemini."""
    st.markdown("""
        <style>
        /* Style général */
        .main {
            background-color: #1a1b26;
            color: #a9b1d6;
        }
        
        /* Container principal */
        .analysis-container {
            background: #24283b;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
            border: 1px solid #414868;
        }
        
        /* Score de qualité */
        .quality-score {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #7aa2f7;
            color: white;
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
        }
        
        /* Métriques */
        .metrics-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric-card {
            background: #1a1b26;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #414868;
        }
        
        /* Code */
        .code-section {
            background: #1a1b26;
            padding: 15px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            margin: 20px 0;
            border: 1px solid #414868;
        }
        
        /* Onglets */
        .tab-container {
            border-bottom: 1px solid #414868;
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 10px 20px;
            color: #a9b1d6;
            cursor: pointer;
            border: none;
            background: none;
        }
        
        .tab.active {
            border-bottom: 2px solid #7aa2f7;
            color: #7aa2f7;
        }
        
        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin: 0 5px;
        }
        
        .badge.good { background: #9ece6a; color: #1a1b26; }
        .badge.warning { background: #e0af68; color: #1a1b26; }
        .badge.error { background: #f7768e; color: #1a1b26; }
        
        /* Boutons */
        .stButton > button {
            background-color: #7aa2f7;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #89b4fa;
            transform: translateY(-1px);
        }
        
        /* Style des boîtes d'issues */
        .issue-box {
            background: #1a1b26;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
            margin: 10px 0;
            text-align: center;
        }
        
        .issue-box.bug {
            border-color: #f7768e;
        }
        
        .issue-box.security {
            border-color: #e0af68;
        }
        
        .issue-box.smell {
            border-color: #9ece6a;
        }
        
        .issue-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .issue-count {
            font-size: 28px;
            font-weight: bold;
            color: #a9b1d6;
        }
        
        .issue-label {
            color: #787c99;
            font-size: 14px;
            margin-top: 5px;
        }
        
        /* Barre de progression */
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #1a1b26;
            border-radius: 2px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #7aa2f7, #9ece6a);
            transition: width 0.3s ease;
        }
        
        /* Style des expanders */
        .streamlit-expanderHeader {
            background-color: #2E2E2E;
            border-radius: 8px;
            padding: 10px 15px;
            color: white;
            font-weight: 500;
            border: none;
            margin-bottom: 10px;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #3E3E3E;
        }
        
        .streamlit-expanderContent {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 15px;
            margin-top: 5px;
            border: 1px solid #3E3E3E;
        }
        
        /* Amélioration de la mise en page */
        .main .block-container {
            padding-top: 2rem;
            max-width: 100%;
        }
        
        .stSidebar .block-container {
            padding-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def show_analysis_report(result: dict):
    """
    Affiche le rapport d'analyse complet.
    
    Args:
        result (dict): Résultats de l'analyse
    """
    st.markdown(
        """
        <style>
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 1.2rem;
                padding: 0 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    tabs = st.tabs([
        "📊 Métriques",
        "🔒 Sécurité",
        "🔍 Analyse",
        "💻 Code"
    ])
    
    with tabs[0]:  # Métriques
        if 'metrics' in result and result['metrics']:
            show_code_metrics(result['metrics'])
            show_code_complexity_chart(result['metrics'])
            show_quality_indicators(result['metrics'])
        else:
            st.info("Aucune métrique disponible pour ce code")
    
    with tabs[1]:  # Sécurité
        if 'security' in result and result['security']:
            if 'issues' in result['security']:
                st.markdown("### 🔒 Problèmes de sécurité")
                if result['security']['issues']:
                    for issue in result['security']['issues']:
                        with st.expander(f"{issue['severity'].upper()}: {issue['title']}"):
                            st.markdown(f"""
                            **Confiance:** {issue['confidence']}  
                            **Description:** {issue['description']}  
                            **Ligne:** {issue['line']}  
                            **Code concerné:**
                            ```python
                            {issue['code']}
                            ```
                            """)
                else:
                    st.success("✅ Aucun problème de sécurité détecté")
            show_code_coverage(result['security'])
        else:
            st.info("Aucune analyse de sécurité disponible pour ce code")
    
    with tabs[2]:  # Analyse
        if 'analysis' in result and result['analysis']:
            st.markdown(
                """
                <div style='background: #2E2E2E; padding: 20px; border-radius: 10px; margin: 10px 0;
                          color: white; line-height: 1.6;'>
                    {}
                </div>
                """.format(result['analysis']),
                unsafe_allow_html=True
            )
        else:
            st.info("Aucune analyse détaillée disponible pour ce code")
    
    with tabs[3]:  # Code
        if 'code' in result and result['code']:
            st.markdown(
                """
                <div style='background: #2E2E2E; border-radius: 10px; margin: 10px 0;
                          font-family: "JetBrains Mono", monospace;'>
                """,
                unsafe_allow_html=True
            )
            show_code_with_highlighting(result['code'])
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aucun code source disponible")
    
    # Actions
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📥 Exporter"):
            # TODO: Implémenter l'export du rapport
            st.info("Export en cours d'implémentation")