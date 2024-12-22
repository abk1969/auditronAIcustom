"""
Visualisations pour l'interface
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import seaborn as sns
from typing import Dict

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

def show_code_metrics(result: dict):
    """Affiche les métriques du code."""
    # Ajouter une validation des données d'entrée
    if not result or 'stats' not in result:
        st.error("Données de métriques invalides")
        return
        
    # Calculer le score dynamiquement
    score = calculate_score(result['stats'])
    
    # Statistiques de base
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Lignes de code",
            result['stats']['Lignes de code'],
            help="Nombre total de lignes de code"
        )
    with col2:
        st.metric(
            "Fonctions",
            result['stats']['Fonctions'],
            help="Nombre de fonctions définies"
        )
    with col3:
        st.metric(
            "Classes",
            result['stats']['Classes'],
            help="Nombre de classes définies"
        )
    with col4:
        st.metric(
            "Score",
            score,
            help="Score global de qualité basé sur les métriques"
        )

    # Graphique principal des statistiques
    st.plotly_chart(
        create_code_stats_chart(result['stats']),
        use_container_width=True
    )

def calculate_score(stats: dict) -> str:
    """Calcule un score basé sur les métriques."""
    # Facteurs de pondération
    weights = {
        'Lignes de code': -0.4,  # Pénalise les fichiers trop longs
        'Fonctions': 0.3,        # Encourage la modularité
        'Classes': 0.3           # Encourage l'orientation objet
    }
    
    # Calcul du score
    score = 100
    for metric, weight in weights.items():
        if metric in stats:
            score += stats[metric] * weight
    
    # Normalisation entre 0 et 100
    score = max(0, min(100, score))
    
    # Conversion en lettre
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    else:
        return 'D'

def show_code_complexity_chart(result: dict):
    """Affiche un graphique de complexité du code."""
    if 'complexity' not in result:
        return
    
    fig = go.Figure()
    
    # Ajouter les métriques de complexité
    fig.add_trace(go.Scatterpolar(
        r=[
            result['complexity'].get('cyclomatic', 0),
            result['complexity'].get('cognitive', 0),
            result['complexity'].get('halstead', 0),
            result['complexity'].get('maintainability', 0),
            result['complexity'].get('loc', 0)
        ],
        theta=['Cyclomatique', 'Cognitive', 'Halstead', 'Maintenabilité', 'LOC'],
        fill='toself',
        name='Complexité'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        template='plotly_dark',
        title={
            'text': 'Métriques de Complexité',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

def show_quality_indicators(result: dict):
    """Affiche les indicateurs de qualité style SonarQube."""
    quality_metrics = {
        'Maintenabilité': {'value': result.get('maintainability', 'A'), 'icon': '🔧'},
        'Fiabilité': {'value': result.get('reliability', 'A'), 'icon': '🎯'},
        'Sécurité': {'value': result.get('security', 'A'), 'icon': '🔒'},
        'Couverture': {'value': f"{result.get('coverage', 0)}%", 'icon': '📊'}
    }
    
    cols = st.columns(len(quality_metrics))
    for col, (metric, data) in zip(cols, quality_metrics.items()):
        with col:
            st.markdown(
                f"""
                <div style='background: #1E1E1E; padding: 20px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 24px;'>{data['icon']}</div>
                    <div style='font-size: 20px; color: {"#00C851" if data["value"] in ["A", "A+"] else "#ff4444"};'>
                        {data['value']}
                    </div>
                    <div style='color: #888; font-size: 14px;'>{metric}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def show_code_issues(result: dict):
    """Affiche les problèmes de code style SonarQube."""
    if 'issues' not in result:
        return
        
    issues = result['issues']
    
    # Compteurs
    bugs = len([i for i in issues if i['type'] == 'bug'])
    vulnerabilities = len([i for i in issues if i['type'] == 'vulnerability'])
    code_smells = len([i for i in issues if i['type'] == 'code_smell'])
    
    # Affichage des compteurs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="issue-box bug">
                <div class="issue-icon">🐛</div>
                <div class="issue-count">{}</div>
                <div class="issue-label">Bugs</div>
            </div>
        """.format(bugs), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="issue-box vulnerability">
                <div class="issue-icon">🔒</div>
                <div class="issue-count">{}</div>
                <div class="issue-label">Vulnérabilités</div>
            </div>
        """.format(vulnerabilities), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="issue-box code-smell">
                <div class="issue-icon">🔍</div>
                <div class="issue-count">{}</div>
                <div class="issue-label">Code Smells</div>
            </div>
        """.format(code_smells), unsafe_allow_html=True)

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

def create_severity_chart(severity_counts: Dict[str, int]) -> go.Figure:
    """
    Crée un graphique de sévérité des problèmes.
    
    Args:
        severity_counts: Dictionnaire contenant le nombre de problèmes par niveau de sévérité
        
    Returns:
        go.Figure: Figure Plotly contenant le graphique
    """
    # Ajout de logging pour debug
    logger.debug(f"Données reçues: {severity_counts}")
    
    if not severity_counts:
        # Créer un graphique vide avec une seule barre
        empty_fig = go.Figure()
        empty_fig.add_trace(go.Bar(
            x=['Aucun problème'],
            y=[0],
            marker_color='#808080'
        ))
        empty_fig.update_layout(
            title="Aucun problème détecté",
            showlegend=False,
            template="plotly_dark",
            height=300,
            margin=dict(t=30, l=0, r=0, b=0)
        )
        return empty_fig

    # Créer les données pour le graphique
    x_data = []
    y_data = []
    colors = []
    color_map = {
        'critical': '#ff0d0d',
        'high': '#ff4e11',
        'medium': '#ff8e15',
        'low': '#fab733'
    }

    # Préparer les données dans l'ordre souhaité
    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in severity_counts:
            x_data.append(severity.upper())
            y_data.append(severity_counts[severity])
            colors.append(color_map[severity])

    # Créer la figure avec une seule trace
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_data,
        y=y_data,
        marker_color=colors,
        text=y_data,
        textposition='auto',
    ))

    # Configurer la mise en page
    fig.update_layout(
        title="Répartition des problèmes par sévérité",
        showlegend=False,
        template="plotly_dark",
        height=300,
        margin=dict(t=30, l=0, r=0, b=0),
        yaxis_title="Nombre de problèmes",
        xaxis_title="Niveau de sévérité"
    )

    return fig