"""Module pour l'affichage des métriques."""
import streamlit as st
from typing import Dict, Any
from AuditronAI.app.security_report import (
    show_metrics, show_grade, show_coverage,
    format_results, show_severity_chart
)

def show_metrics_tab(security_results: Dict[str, Any]):
    """Affiche l'onglet des métriques."""
    st.markdown("## 📊 Métriques du code")
    
    # Afficher les métriques principales
    show_metrics(security_results)
    
    # Afficher la note globale
    col1, col2 = st.columns([1, 3])
    with col1:
        show_grade(security_results)
    with col2:
        show_coverage(security_results)
    
    # Afficher le résumé formaté
    st.markdown(format_results(security_results))
    
    # Afficher le graphique des sévérités
    st.plotly_chart(
        show_severity_chart(security_results['summary']['severity_counts']),
        use_container_width=True
    ) 