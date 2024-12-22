"""
Configuration des API (OpenAI/Google)
"""
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv, set_key
import os

def update_env_file(new_values: dict):
    """Met à jour le fichier .env avec de nouvelles valeurs."""
    env_path = Path(".env")
    
    # Lire le fichier .env existant
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Convertir les lignes en dictionnaire
    current_env = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            current_env[key.strip()] = value.strip()
    
    # Mettre à jour avec les nouvelles valeurs
    current_env.update(new_values)
    
    # Réécrire le fichier .env
    with open(env_path, 'w') as f:
        for key, value in current_env.items():
            f.write(f"{key}={value}\n")
    
    # Recharger les variables d'environnement
    load_dotenv(override=True)

def show_api_settings():
    """Affiche les paramètres API dans la sidebar."""
    st.markdown("### 🔑 Configuration API")
    
    # Sélection du service AI
    service = st.selectbox(
        "Service AI",
        ["OpenAI", "Google Gemini"],
        index=0 if os.getenv("AI_SERVICE", "openai").lower() == "openai" else 1
    )
    
    # Configuration selon le service sélectionné
    if service == "OpenAI":
        api_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password"
        )
        model = st.selectbox(
            "Modèle",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
        if st.button("💾 Sauvegarder config OpenAI"):
            update_env_file({
                "AI_SERVICE": "openai",
                "OPENAI_API_KEY": api_key,
                "OPENAI_MODEL": model
            })
            st.success("Configuration OpenAI sauvegardée!")
            
    else:  # Google Gemini
        api_key = st.text_input(
            "Google API Key",
            value=os.getenv("GOOGLE_API_KEY", ""),
            type="password"
        )
        model = st.selectbox(
            "Modèle",
            ["gemini-2.0-flash-exp", "gemini-pro", "gemini-pro-vision"],
            index=0
        )
        if st.button("💾 Sauvegarder config Gemini"):
            update_env_file({
                "AI_SERVICE": "google",
                "GOOGLE_API_KEY": api_key,
                "GOOGLE_MODEL": model
            })
            st.success("Configuration Gemini sauvegardée!") 