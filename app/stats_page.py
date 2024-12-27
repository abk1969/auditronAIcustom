import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, Any
from AuditronAI.core.history import AnalysisHistory
from AuditronAI.core.usage_stats import UsageStats
from AuditronAI.app.security_report import (
    show_metrics, show_grade, show_coverage,
    format_results, show_severity_chart
)
from AuditronAI.app.metrics import show_metrics_tab
from .navigation import show_stats_navigation

def format_timestamp(timestamp: str) -> str:
    """Formate un timestamp en date lisible."""
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%d/%m/%Y %H:%M")

def show_statistics_page(history: AnalysisHistory, usage_stats: UsageStats):
    """Affiche la page des statistiques."""
    st.title("📊 Statistiques")

    # Ajouter le bouton d'export dans la sidebar
    export_stats(history)

    # Statistiques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Analyses totales",
            len(history.get_records()),
            help="Nombre total d'analyses effectuées"
        )
    
    with col2:
        avg_score = sum(entry.score for entry in history.get_records()) / len(history.get_records()) if history.get_records() else 0
        st.metric(
            "Score moyen",
            f"{avg_score:.1f}/100",
            help="Score de sécurité moyen"
        )
    
    with col3:
        total_issues = sum(entry.issues_count for entry in history.get_records())
        st.metric(
            "Problèmes détectés",
            total_issues,
            help="Total des problèmes trouvés"
        )
    
    with col4:
        total_functions = sum(len(entry.details.get('functions', [])) for entry in history.get_records())
        st.metric(
            "Fonctions analysées",
            total_functions,
            help="Nombre total de fonctions analysées"
        )

    # Ajouter des tendances et des comparaisons
    if len(history.get_records()) > 1:
        st.subheader("📊 Analyse des tendances")
        
        # Calculer les tendances
        scores = [entry.score for entry in history.get_records()]
        last_score = scores[-1]
        avg_score = sum(scores) / len(scores)
        trend = "↗️" if last_score > avg_score else "↘️"
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Tendance du score",
                f"{last_score:.1f}/100",
                f"{trend} {(last_score - avg_score):.1f}",
                help="Comparaison avec la moyenne"
            )
        
        with col2:
            # Calculer le taux de réussite
            success_rate = sum(1 for s in scores if s >= 80) / len(scores) * 100
            st.metric(
                "Taux de réussite",
                f"{success_rate:.1f}%",
                help="Pourcentage de scores >= 80/100"
            )

    # Ajouter des graphiques d'analyse
    st.subheader("📈 Tendances")
    
    col1, col2 = st.columns(2)
    with col1:
        # Graphique d'évolution des scores
        scores = [entry.score for entry in history.get_records()]
        dates = [entry.timestamp for entry in history.get_records()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Score de sécurité'
        ))
        fig.update_layout(
            title="Évolution des scores de sécurité",
            template="plotly_dark",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique des types de problèmes
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for entry in history.get_records():
            counts = entry.details.get('severity_counts', {})
            for severity, count in counts.items():
                severity_counts[severity] += count
        
        st.plotly_chart(
            show_severity_chart(severity_counts),
            use_container_width=True
        )

    # Historique des analyses avec filtres
    if history.get_records():
        st.subheader("📈 Historique des analyses")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider(
                "Score minimum",
                0, 100, 0,
                help="Filtrer par score minimum"
            )
        with col2:
            show_only_issues = st.checkbox(
                "Afficher uniquement les analyses avec problèmes",
                help="Ne montrer que les analyses ayant des problèmes de sécurité"
            )
        
        # Filtrer et afficher les entrées
        filtered_entries = [
            entry for entry in history.get_records()
            if entry.score >= min_score
            and (not show_only_issues or entry.issues_count > 0)
        ]
        
        for entry in reversed(filtered_entries):
            with st.expander(
                f"📄 {entry.filename} - Score: {entry.score:.1f}/100 "
                f"({format_timestamp(str(entry.timestamp))})"
            ):
                show_metrics_tab(entry.details)
    else:
        st.info("Aucune analyse effectuée pour le moment")

def show_overview_stats(df):
    """Affiche les statistiques générales."""
    st.subheader("Vue d'ensemble des analyses")
    
    # Statistiques de base
    total_analyses = len(df)
    unique_services = df['service'].nunique() if 'service' in df.columns else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total des analyses", total_analyses)
    with col2:
        st.metric("Services utilisés", unique_services)
    with col3:
        st.metric("Fichiers analysés", df['file'].nunique())

    # Graphique des analyses par jour
    df['date'] = df['timestamp'].dt.date
    analyses_by_date = df.groupby('date').size().reset_index(name='count')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=analyses_by_date['date'],
        y=analyses_by_date['count'],
        name="Analyses"
    ))
    
    fig.update_layout(
        title="Analyses par jour",
        xaxis_title="Date",
        yaxis_title="Nombre d'analyses",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_temporal_analysis(df):
    """Affiche l'analyse temporelle des données."""
    st.subheader("Analyse temporelle")
    
    # Graphique d'évolution des scores dans le temps
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['score'],
        mode='lines+markers',
        name='Score'
    ))
    fig.update_layout(
        title="Évolution des scores dans le temps",
        xaxis_title="Date",
        yaxis_title="Score"
    )
    st.plotly_chart(fig) 

def show_service_comparison(df):
    """Affiche la comparaison entre les services."""
    st.subheader("Comparaison des services")
    
    if 'service' not in df.columns:
        st.warning("Aucune donnée de service disponible")
        return
    
    # Analyses par service
    service_stats = df.groupby('service').agg({
        'file': 'count',
        'timestamp': 'max'
    }).reset_index()
    
    service_stats.columns = ['Service', 'Nombre analyses', 'Dernière utilisation']
    service_stats['Dernière utilisation'] = service_stats['Dernière utilisation'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Graphique avec tooltips
    fig = go.Figure(data=[
        go.Bar(
            x=service_stats['Service'],
            y=service_stats['Nombre analyses'],
            text=service_stats['Nombre analyses'],
            textposition='auto',
            hovertemplate=(
                "<b>%{x}</b><br>" +
                "Analyses: %{y}<br>" +
                "Dernière utilisation: %{customdata}<br>" +
                "<extra></extra>"
            ),
            customdata=service_stats['Dernière utilisation']
        )
    ])
    fig.update_layout(
        title="Analyses par service",
        xaxis_title="Service",
        yaxis_title="Nombre d'analyses",
        template="plotly_dark",
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.write("Détails par service:")
    st.dataframe(service_stats)

def show_detailed_history(df):
    """Affiche l'historique détaillé des analyses."""
    st.subheader("Historique détaillé")
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        service_filter = st.multiselect(
            "Filtrer par service",
            options=sorted(df['service'].unique()) if 'service' in df.columns else []
        )
    with col2:
        date_range = st.date_input(
            "Période",
            [df['timestamp'].min().date(), df['timestamp'].max().date()]
        )
    
    # Appliquer les filtres
    filtered_df = df.copy()
    if service_filter:
        filtered_df = filtered_df[filtered_df['service'].isin(service_filter)]
    filtered_df = filtered_df[
        (filtered_df['timestamp'].dt.date >= date_range[0]) &
        (filtered_df['timestamp'].dt.date <= date_range[1])
    ]
    
    # Sélectionner les colonnes à afficher
    display_columns = ['timestamp', 'file', 'service']
    
    # Afficher les données avec pagination
    page_size = 10
    total_pages = len(filtered_df) // page_size + (1 if len(filtered_df) % page_size > 0 else 0)
    
    if total_pages > 0:
        page = st.selectbox("Page", range(1, total_pages + 1)) - 1
        start_idx = page * page_size
        end_idx = start_idx + page_size
        
        display_df = filtered_df[display_columns].iloc[start_idx:end_idx].copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(display_df)
    else:
        st.warning("Aucune donnée ne correspond aux critères de filtrage.")

def show_stats_navigation():
    """Affiche la navigation des statistiques."""
    return st.sidebar.radio(
        label="Type de statistiques",
        options=[
            "Vue d'ensemble",
            "Analyse temporelle",
            "Comparaison des services",
            "Métriques de code",
            "Historique détaillé"
        ],
        label_visibility="visible"
    )

def show_code_metrics(df):
    """Affiche les métriques de code."""
    st.subheader("Métriques de code")
    
    if 'code_metrics' in df.columns:
        metrics_df = pd.json_normalize(df['code_metrics'])
        
        # Moyennes des métriques
        st.write("Moyennes des métriques de code:")
        col1, col2, col3 = st.columns(3)
        metrics = list(metrics_df.columns)
        for idx, metric in enumerate(metrics):
            with [col1, col2, col3][idx % 3]:
                mean_value = metrics_df[metric].mean()
                st.metric(metric, f"{mean_value:.2f}")
        
        # Évolution des métriques
        selected_metric = st.selectbox("Sélectionner une métrique", metrics)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=metrics_df[selected_metric],
            mode='lines+markers',
            name=selected_metric
        ))
        fig.update_layout(
            title=f"Évolution de {selected_metric}",
            xaxis_title="Date",
            yaxis_title="Valeur"
        )
        st.plotly_chart(fig)
    else:
        st.warning("Aucune métrique de code disponible")

def load_analysis_history():
    """Charge l'historique des analyses."""
    history_file = Path("datasets") / "analysis_history.json"
    if not history_file.exists():
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_analysis_history(history):
    """Sauvegarde l'historique des analyses."""
    history_file = Path("datasets") / "analysis_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def export_stats(history: AnalysisHistory):
    """Permet d'exporter les statistiques."""
    st.sidebar.markdown("### 📥 Exporter les statistiques")
    
    export_format = st.sidebar.selectbox(
        "Format d'export",
        ["Excel", "PDF"],
        help="Choisir le format d'export"
    )
    
    if st.sidebar.button("📥 Exporter"):
        entries = history.get_records()
        
        if export_format == "Excel":
            df = pd.DataFrame([{
                'Date': format_timestamp(str(entry.timestamp)),
                'Fichier': entry.filename,
                'Score': entry.score,
                'Problèmes': entry.issues_count,
                'Complexité': entry.complexity,
                'Détails': entry.details
            } for entry in entries])
            
            st.sidebar.download_button(
                "📥 Télécharger Excel",
                df.to_csv(index=False).encode('utf-8'),
                "statistiques.csv",
                "text/csv",
                key='download-csv'
            )
            st.sidebar.success("✅ Export Excel prêt au téléchargement")
        else:
            st.sidebar.warning("Export PDF à venir")