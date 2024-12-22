"""Module de génération des rapports de sécurité."""
import streamlit as st
from typing import Dict, Any

from .visualizations import create_severity_chart
from AuditronAI.core.logger import logger


def show_security_report(results: Dict[str, Any]) -> None:
    """
    Affiche le rapport complet d'analyse de sécurité.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        st.markdown(results['explanation'])
        
        col1, col2 = st.columns(2)
        with col1:
            show_metrics(results)
        with col2:
            show_grade(results)
        
        # Log pour debug
        severity_counts = results.get('summary', {}).get('severity_counts', {})
        logger.debug(f"Données de sévérité avant graphique : {severity_counts}")
        show_severity_chart(severity_counts)
        show_coverage(results)
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du rapport : {str(e)}")
        st.error("Une erreur est survenue lors de l'affichage du rapport.")


def show_metrics(results: Dict[str, Any]) -> None:
    """
    Affiche les métriques principales.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        summary = results.get('summary', {})
        
        st.metric(
            label="Score de sécurité",
            value=f"{summary.get('score', 0):.1f}/100",
            delta=None
        )
        
        st.metric(
            label="Problèmes détectés",
            value=summary.get('total_issues', 0),
            delta=None
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des métriques : {str(e)}")
        st.error("Impossible d'afficher les métriques")


def show_grade(results: Dict[str, Any]) -> None:
    """
    Affiche la note de sécurité.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
    """
    try:
        score = results.get('summary', {}).get('score', 0)
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


def show_coverage(results: Dict[str, Any]) -> None:
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
                value=len(results.get('security_issues', [])),
                delta=None
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de la couverture : {str(e)}")
        st.error("Impossible d'afficher la couverture")


def format_results(results: Dict[str, Any]) -> str:
    """
    Formate les résultats pour l'affichage.
    
    Args:
        results: Dictionnaire contenant les résultats de l'analyse
        
    Returns:
        str: Texte formaté contenant le résumé des résultats
    """
    try:
        summary = results.get('summary', {})
        code_quality = results.get('code_quality', {})
        
        return (
            f"### Résultats de l'analyse\n\n"
            f"Score de sécurité : {summary.get('score', 0):.1f}/100\n"
            f"Problèmes détectés : {summary.get('total_issues', 0)}\n"
            f"Complexité moyenne : {code_quality.get('complexity', 0):.1f}\n\n"
            f"{summary.get('details', 'Aucun détail disponible')}"
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


def validate_results(results: Dict[str, Any]) -> bool:
    """
    Valide la structure des résultats.
    
    Args:
        results: Résultats à valider
        
    Returns:
        bool: True si les résultats sont valides
    """
    required_keys = {'file', 'security_issues', 'code_quality', 'summary'}
    if not all(key in results for key in required_keys):
        logger.error(f"Structure de résultats invalide. Clés manquantes : {required_keys - set(results.keys())}")
        return False

    summary = results.get('summary', {})
    if not isinstance(summary.get('severity_counts'), dict):
        logger.error("Format de severity_counts invalide")
        return False

    return True