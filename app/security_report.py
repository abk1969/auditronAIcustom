"""Module de génération des rapports de sécurité."""
import streamlit as st
from typing import Dict
import plotly.graph_objects as go

from .visualizations import create_severity_chart
from AuditronAI.core.logger import logger
from AuditronAI.core.analysis_results import AnalysisResults
from AuditronAI.core.metrics.code_metrics import ModuleMetrics

def show_security_report(results: AnalysisResults) -> None:
    """
    Affiche le rapport complet d'analyse de sécurité.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        # Afficher les métriques
        if results.code:
            show_metrics(results.code, results.filename)
        
        # Afficher les problèmes de sécurité
        if results.security_issues:
            st.markdown("## 🔒 Problèmes de sécurité détectés")
            for issue in results.security_issues:
                with st.expander(f"{issue['severity'].upper()}: {issue['message']}"):
                    st.markdown(f"""
                    **Type:** {issue['type']}  
                    **Ligne:** {issue.get('line', 'N/A')}  
                    **Code concerné:**
                    ```python
                    {issue.get('code', 'Code non disponible')}
                    ```
                    """)
        else:
            st.success("✅ Aucun problème de sécurité détecté")
        
        # Créer et afficher le graphique
        try:
            severity_counts = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            # Compter les problèmes par sévérité
            for issue in results.security_issues:
                severity = issue['severity'].lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Créer et afficher le graphique
            fig = create_severity_chart(severity_counts)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du graphique : {str(e)}")
            st.warning("Une erreur s'est produite lors de l'affichage du graphique")
            
        st.markdown(format_results(results))
        
        col1, col2 = st.columns(2)
        with col1:
            show_metrics(results)
        with col2:
            show_grade(results)
        
        show_coverage(results)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du rapport : {str(e)}")
        st.error("Une erreur est survenue lors de l'affichage du rapport.")


def show_metrics(results: AnalysisResults) -> None:
    """
    Affiche les métriques principales.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        st.metric(
            label="Score de sécurité",
            value=f"{results.summary['score']:.1f}/100",
            delta=None
        )
        
        st.metric(
            label="Problèmes détectés",
            value=results.summary['total_issues'],
            delta=None
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des métriques : {str(e)}")
        st.error("Impossible d'afficher les métriques")


def show_metrics(code: str, filename: str) -> None:
    """Affiche les métriques du code."""
    try:
        metrics = ModuleMetrics(code, filename)
        m = metrics.metrics()
        
        # Métriques globales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lignes de code", m['loc'])
        with col2:
            st.metric("Complexité cognitive", m['cognitive_complexity'])
        with col3:
            st.metric("Maintenabilité", f"{m['maintainability_index']:.1f}")
            
        # Fonctions complexes
        complex_funcs = metrics.get_complex_functions()
        if complex_funcs:
            st.warning("Fonctions complexes détectées")
            for func in complex_funcs:
                st.code(f"{func.name} (complexité: {func.complexity})")
                
        # Fonctions longues
        long_funcs = metrics.get_long_functions()
        if long_funcs:
            st.warning("Fonctions longues détectées")
            for func in long_funcs:
                st.code(f"{func.name} ({func.lines} lignes)")
                
        # Fonctions imbriquées
        nested_funcs = metrics.get_deeply_nested_functions()
        if nested_funcs:
            st.warning("Fonctions trop imbriquées détectées")
            for func in nested_funcs:
                st.code(f"{func.name} (profondeur: {func.nested_depth})")
                
    except Exception as e:
        logger.error(f"Erreur lors du calcul des métriques : {str(e)}")
        st.error("Impossible de calculer les métriques pour ce fichier")


def show_grade(results: AnalysisResults) -> None:
    """
    Affiche la note de sécurité.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        score = results.summary['score']
        grade = get_grade(score)
        
        st.metric(
            label="Note globale",
            value=grade,
            delta=None
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de la note : {str(e)}")
        st.metric(
            label="Note globale",
            value="N/A",
            delta=None
        )


def get_grade(score: float) -> str:
    """
    Calcule la note en fonction du score.
    
    Args:
        score: Score de sécurité entre 0 et 100
        
    Returns:
        str: Note sous forme de lettre (A+, A, B, C, D, F)
    """
    if score >= 95:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 65:
        return "C"
    elif score >= 55:
        return "D"
    return "F"


def show_coverage(results: AnalysisResults) -> None:
    """
    Affiche la couverture de l'analyse.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        st.subheader("Couverture de l'analyse")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Fichiers analysés",
                value=1,
                delta=None
            )
        with col2:
            st.metric(
                label="Outils utilisés",
                value=4,
                delta=None
            )
        with col3:
            st.metric(
                label="Tests effectués",
                value=len(results.security_issues),
                delta=None
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de la couverture : {str(e)}")
        st.error("Impossible d'afficher la couverture")


def format_results(results: AnalysisResults) -> str:
    """
    Formate les résultats pour l'affichage.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
        
    Returns:
        str: Texte formaté contenant le résumé des résultats
    """
    try:
        return (
            f"### Résultats de l'analyse\n\n"
            f"Score de sécurité : {results.summary['score']:.1f}/100\n"
            f"Problèmes détectés : {results.summary['total_issues']}\n"
            f"Complexité moyenne : {results.code_quality.complexity:.1f}\n\n"
            f"{results.summary['details']}"
        )
    except Exception as e:
        logger.error(f"Erreur lors du formatage des résultats : {str(e)}")
        return "### Erreur lors de la génération du rapport"


def show_severity_chart(severity_counts: Dict[str, int]) -> None:
    """
    Affiche le graphique de sévérité des problèmes.
    
    Args:
        severity_counts: Dictionnaire contenant le nombre de problèmes par niveau de sévérité
    """
    try:
        # Ajout de logging pour debug
        logger.debug(f"Tentative de création du graphique avec: {severity_counts}")
        
        fig = create_severity_chart(severity_counts)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Impossible de créer le graphique de sévérité")
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique : {str(e)}")
        st.error("Impossible d'afficher le graphique de sévérité")


def validate_results(results: AnalysisResults) -> bool:
    """
    Valide la structure des résultats.
    
    Args:
        results: Résultats à valider
        
    Returns:
        bool: True si les résultats sont valides
    """
    try:
        if not results.file or not isinstance(results.summary['severity_counts'], dict):
            logger.error("Structure de résultats invalide")
            return False
        return True
    except (AttributeError, KeyError) as e:
        logger.error(f"Validation des résultats échouée: {str(e)}")
        return False
