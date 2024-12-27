#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import getpass
from pathlib import Path
import secrets
import string
from typing import Dict, Optional

def check_python_version():
    """Vérifie que la version de Python est compatible."""
    if not (3, 9, 0) <= sys.version_info < (3, 10, 0):
        print("❌ Python 3.9.x est requis")
        print(f"Version actuelle: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        sys.exit(1)
    print("✅ Version Python compatible détectée")

def install_poetry():
    """Installe Poetry s'il n'est pas déjà installé."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry est déjà installé")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installation de Poetry...")
        subprocess.run(
            ["curl", "-sSL", "https://install.python-poetry.org", "|", "python3", "-"],
            shell=True,
            check=True
        )
        print("✅ Poetry installé avec succès")

def get_api_key(service: str) -> str:
    """Demande de manière sécurisée une clé API à l'utilisateur."""
    while True:
        key = getpass.getpass(f"Entrez votre clé API {service} (laissez vide pour passer): ")
        if not key:
            return ""
        if len(key) > 20:  # Vérification basique de la longueur
            return key
        print(f"❌ La clé {service} semble invalide. Veuillez réessayer.")

def generate_secret_key(length: int = 32) -> str:
    """Génère une clé secrète aléatoire."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file(project_root: Path, api_keys: Dict[str, str]):
    """Crée le fichier .env avec les variables d'environnement."""
    env_path = project_root / ".env"
    secret_key = generate_secret_key()
    
    env_content = f"""# Configuration AuditronAI
AI_SERVICE={"google" if api_keys["google"] else "openai" if api_keys["openai"] else "google"}
OPENAI_API_KEY={api_keys["openai"]}
GOOGLE_API_KEY={api_keys["google"]}
SECRET_KEY={secret_key}

# Configuration base de données
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auth_db
DB_USER=postgres
DB_PASSWORD=postgres

# Configuration interface
STREAMLIT_THEME_BASE=dark
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
UI_DEFAULT_THEME=dark

# Configuration sécurité
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
STREAMLIT_EXTERNAL_ACCESS=false
DEBUG=false
"""
    
    env_path.write_text(env_content)
    print(f"✅ Fichier .env créé: {env_path}")

def create_streamlit_secrets(project_root: Path, api_keys: Dict[str, str]):
    """Crée le fichier de secrets Streamlit."""
    secrets_dir = project_root / ".streamlit"
    secrets_dir.mkdir(exist_ok=True)
    secrets_path = secrets_dir / "secrets.toml"
    
    secrets_content = f"""
[api_keys]
openai = "{api_keys['openai']}"
google = "{api_keys['google']}"

[database]
host = "localhost"
port = 5432
db = "auth_db"
user = "postgres"
password = "postgres"
"""
    
    secrets_path.write_text(secrets_content)
    print(f"✅ Fichier secrets.toml créé: {secrets_path}")

def setup_project_structure(project_root: Path):
    """Crée la structure de dossiers nécessaire."""
    dirs = ["logs", "data"]
    for dir_name in dirs:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
    print("✅ Structure de dossiers créée")

def install_dependencies(project_root: Path):
    """Installe les dépendances du projet avec Poetry."""
    print("📦 Installation des dépendances...")
    subprocess.run(["poetry", "install"], cwd=project_root, check=True)
    print("✅ Dépendances installées")

def install_postgres():
    """Installe et configure PostgreSQL."""
    print("🐘 Installation de PostgreSQL...")
    # Import et exécution du script d'installation PostgreSQL
    from install_postgres import main as install_postgres_main
    install_postgres_main()
    print("✅ PostgreSQL installé et configuré")

def main():
    try:
        project_root = Path(__file__).parent.parent.parent
        
        print("\n=== Installation d'AuditronAI ===\n")
        
        # Vérification des prérequis
        check_python_version()
        install_poetry()
        
        # Installation de PostgreSQL
        install_postgres()
        
        # Collecte des clés API
        print("\n=== Configuration des API ===\n")
        api_keys = {
            "openai": get_api_key("OpenAI"),
            "google": get_api_key("Google AI")
        }
        
        if not any(api_keys.values()):
            print("⚠️ Aucune clé API fournie. L'application fonctionnera en mode limité.")
        
        # Création de la structure du projet
        setup_project_structure(project_root)
        
        # Configuration des secrets
        create_env_file(project_root, api_keys)
        create_streamlit_secrets(project_root, api_keys)
        
        # Installation des dépendances
        install_dependencies(project_root)
        
        print("\n=== Installation terminée avec succès! ===\n")
        print("Pour lancer l'application:")
        print("1. Activez l'environnement Poetry:")
        print("   poetry shell")
        print("2. Lancez l'application:")
        print("   poetry run run-app")
        print("\nL'application sera accessible à l'adresse: http://localhost:8501")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'installation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
