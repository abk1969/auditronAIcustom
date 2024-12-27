"""Module de visualisation des données."""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import seaborn as sns
from typing import Dict, Any, Optional, List, Union

from AuditronAI.core.logger import logger

def create_code_stats_chart(stats: dict):
    """Crée un graphique des statistiques du code avec Plotly."""
    # Ajouter une validation des données d'entrée
    if not stats:
        raise ValueError("Le dictionnaire de statistiques ne peut pas être vide")
    
    # Préparer les données
    df = pd.DataFrame({
        'Métrique': list(stats.keys()),
        'Valeur': list(stats.values())
    })
    
    # Créer le graphique avec Plotly
    fig = go.Figure()
    
    # Ajouter les barres
    fig.add_trace(go.Bar(
        x=df['Métrique'],
        y=df['Valeur'],
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        text=df['Valeur'],
        textposition='auto',
    ))
    
    # Personnaliser le thème
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(26, 27, 38, 0.8)',
        paper_bgcolor='rgba(26, 27, 38, 0.8)',
        title={
            'text': 'Statistiques du Code',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color='white')
        },
        xaxis=dict(
            title='Métrique',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white'),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.2)'
        ),
        yaxis=dict(
            title='Nombre',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(size=12, color='white'),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.2)'
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50),
        height=400
    )
    
    return fig

def show_code_metrics(metrics: dict):
    """
    Affiche les métriques du code.
    
    Args:
        metrics: Dictionnaire contenant les métriques du code
    """
    if not metrics:
        st.warning("Aucune métrique disponible")
        return
        
    # Afficher les métriques de base
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Lignes de code",
            metrics.get('loc', 0),
            help="Nombre total de lignes de code"
        )
    with col2:
        st.metric(
            "Fonctions",
            metrics.get('functions', 0),
            help="Nombre de fonctions définies"
        )
    with col3:
        st.metric(
            "Classes",
            metrics.get('classes', 0),
            help="Nombre de classes définies"
        )
    with col4:
        st.metric(
            "Complexité",
            metrics.get('complexity', 0),
            help="Complexité cyclomatique moyenne"
        )
        
    # Créer le graphique des métriques
    try:
        df = pd.DataFrame({
            'Métrique': ['LOC', 'Fonctions', 'Classes', 'Complexité'],
            'Valeur': [
                metrics.get('loc', 0),
                metrics.get('functions', 0),
                metrics.get('classes', 0),
                metrics.get('complexity', 0)
            ]
        })
        
        fig = px.bar(
            df,
            x='Métrique',
            y='Valeur',
            color='Métrique',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )
        
        fig.update_layout(
            template='plotly_dark',
            showlegend=False,
            title="Distribution des métriques",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique: {str(e)}")
        st.error("Impossible de créer le graphique des métriques")

def show_code_complexity_chart(metrics: dict):
    """
    Affiche un graphique de complexité du code.
    
    Args:
        metrics: Dictionnaire contenant les métriques de complexité
    """
    if not metrics or 'complexity' not in metrics:
        return
        
    try:
        complexity = metrics['complexity']
        
        # Créer une échelle de couleur basée sur la complexité
        if complexity < 5:
            color = '#4ECDC4'  # Vert
        elif complexity < 10:
            color = '#FFD93D'  # Jaune
        else:
            color = '#FF6B6B'  # Rouge
            
        # Créer le graphique
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=complexity,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 5], 'color': '#E8F8F5'},
                    {'range': [5, 10], 'color': '#FDEBD0'},
                    {'range': [10, 20], 'color': '#FADBD8'}
                ]
            }
        ))
        
        fig.update_layout(
            title="Complexité du Code",
            height=300,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique de complexité: {str(e)}")

def show_quality_indicators(metrics: dict):
    """
    Affiche les indicateurs de qualité style SonarQube.
    
    Args:
        metrics: Dictionnaire contenant les métriques de qualité
    """
    if not metrics:
        return
        
    quality_score = min(100, max(0, (
        (metrics.get('loc', 0) > 0) * 25 +
        (metrics.get('functions', 0) > 0) * 25 +
        (metrics.get('classes', 0) > 0) * 25 +
        (metrics.get('complexity', 0) < 10) * 25
    )))
    
    st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
            <div style='display: inline-block; background: {get_quality_color(quality_score)}; 
                      padding: 10px 20px; border-radius: 15px; color: white;'>
                Score de Qualité: {quality_score}/100
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_quality_color(score: float) -> str:
    """
    Retourne une couleur basée sur le score de qualité.
    
    Args:
        score: Score de qualité entre 0 et 100
        
    Returns:
        Code couleur hexadécimal
    """
    if score >= 80:
        return '#4ECDC4'  # Vert
    elif score >= 60:
        return '#FFD93D'  # Jaune
    else:
        return '#FF6B6B'  # Rouge

def show_code_issues(security_data: dict):
    """
    Affiche les problèmes de code style SonarQube.
    
    Args:
        security_data: Données de sécurité du code
    """
    if not security_data or 'issues' not in security_data:
        return
        
    issues = security_data['issues']
    
    if not issues:
        st.success("✅ Aucun problème détecté")
        return
        
    # Compter les problèmes par sévérité
    severity_counts = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for issue in issues:
        severity = issue.get('severity', 'low').lower()
        if severity in severity_counts:
            severity_counts[severity] += 1
            
    # Créer et afficher le graphique de sévérité
    try:
        fig = create_severity_chart(severity_counts)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique de sévérité: {str(e)}")

def create_severity_chart(severity_counts: Dict[str, Any]) -> go.Figure:
    """
    Crée un graphique de sévérité des problèmes.
    
    Args:
        severity_counts: Dictionnaire contenant le nombre de problèmes par niveau de sévérité
        
    Returns:
        go.Figure: Figure Plotly contenant le graphique
    """
    try:
        # Créer un graphique vide par défaut
        empty_fig = go.Figure(data=[
            go.Bar(
                x=['AUCUN PROBLÈME'],
                y=[0],
                marker_color='#808080',
                text=['0'],
                textposition='auto',
            )
        ])
        empty_fig.update_layout(
            title="Aucun problème détecté",
            showlegend=False,
            template="plotly_dark",
            height=300,
            margin=dict(t=30, l=0, r=0, b=0)
        )

        # Si pas de données valides, retourner le graphique vide
        if not severity_counts or not isinstance(severity_counts, dict):
            logger.warning("Données de sévérité invalides")
            return empty_fig

        # Calculer le total des problèmes
        total_issues = sum(severity_counts.values())
        
        # Si aucun problème, retourner le graphique vide
        if total_issues == 0:
            return empty_fig

        # Créer les listes pour le graphique
        severities = []
        counts = []
        colors = []
        
        # Définir les couleurs pour chaque niveau de sévérité
        color_map = {
            'critical': '#ff0d0d',
            'high': '#ff4e11',
            'medium': '#ff8e15',
            'low': '#fab733'
        }
        
        # Préparer les données pour le graphique
        for severity, count in severity_counts.items():
            if count > 0:
                severities.append(severity.upper())
                counts.append(count)
                colors.append(color_map.get(severity.lower(), '#808080'))

        # Créer le graphique
        fig = go.Figure(data=[
            go.Bar(
                x=severities,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto',
            )
        ])

        # Configurer la mise en page
        fig.update_layout(
            title="Répartition des problèmes par sévérité",
            showlegend=False,
            template="plotly_dark",
            height=300,
            margin=dict(t=30, l=0, r=0, b=0),
            yaxis_title="Nombre de problèmes",
            xaxis_title="Niveau de sévérité",
            bargap=0.15,
        )
        
        return fig
            
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique : {str(e)}")
        return empty_fig

def show_code_coverage(result: dict):
    """Affiche la couverture de code."""
    if 'coverage' not in result:
        return
        
    coverage = result['coverage']
    
    # Graphique de couverture
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = coverage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00C851" if coverage >= 80 else "#ff4444"},
            'steps': [
                {'range': [0, 50], 'color': "#ff4444"},
                {'range': [50, 80], 'color': "#ffbb33"},
                {'range': [80, 100], 'color': "#00C851"}
            ]
        }
    ))
    
    fig.update_layout(
        title="Couverture de Code",
        template="plotly_dark",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)