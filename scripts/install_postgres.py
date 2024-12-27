import os
import sys
import platform
import subprocess
import urllib.request
import shutil
import tempfile
from pathlib import Path

def get_postgres_installer_url():
    system = platform.system().lower()
    if system == "windows":
        return "https://get.enterprisedb.com/postgresql/postgresql-15.5-1-windows-x64.exe"
    elif system == "darwin":  # MacOS
        return "https://get.enterprisedb.com/postgresql/postgresql-15.5-1-osx.dmg"
    elif system == "linux":
        # Pour Linux, on utilisera le gestionnaire de paquets
        return None
    else:
        raise OSError(f"Système d'exploitation non supporté: {system}")

def download_file(url, dest_path):
    print(f"Téléchargement de PostgreSQL depuis {url}...")
    urllib.request.urlretrieve(url, dest_path)

def install_postgres_windows(installer_path):
    # Installation silencieuse avec les paramètres par défaut
    install_cmd = [
        installer_path,
        "--mode", "unattended",
        "--superpassword", "postgres",
        "--serverport", "5432",
        "--locale", "fr_FR"
    ]
    subprocess.run(install_cmd, check=True)

def install_postgres_macos(installer_path):
    # Monter le DMG
    mount_point = "/Volumes/PostgreSQL"
    subprocess.run(["hdiutil", "attach", installer_path], check=True)
    
    # Installer le package
    pkg_path = "/Volumes/PostgreSQL/postgresql-15.5-1-osx.pkg"
    subprocess.run(["sudo", "installer", "-pkg", pkg_path, "-target", "/"], check=True)
    
    # Démonter le DMG
    subprocess.run(["hdiutil", "detach", mount_point], check=True)

def install_postgres_linux():
    # Ajout du dépôt PostgreSQL
    subprocess.run([
        "sudo", "sh", "-c",
        "echo 'deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main' > /etc/apt/sources.list.d/pgdg.list"
    ], check=True)
    
    # Import de la clé de signature
    subprocess.run([
        "wget", "--quiet", "-O", "-",
        "https://www.postgresql.org/media/keys/ACCC4CF8.asc",
        "|", "sudo", "apt-key", "add", "-"
    ], check=True)
    
    # Installation
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "postgresql-15"], check=True)

def configure_postgres():
    system = platform.system().lower()
    
    if system == "windows":
        pg_bin = r"C:\Program Files\PostgreSQL\15\bin"
        if pg_bin not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + pg_bin
    
    # Création de la base de données et de l'utilisateur
    commands = [
        "createdb auth_db",
        "psql -d auth_db -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
    ]
    
    for cmd in commands:
        try:
            if system == "windows":
                subprocess.run(cmd, shell=True, check=True)
            else:
                subprocess.run(f"sudo -u postgres {cmd}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande {cmd}: {e}")
            if "already exists" not in str(e):
                raise

def initialize_database():
    # Lecture du script SQL
    current_dir = Path(__file__).parent.parent.parent
    init_sql_path = current_dir / "init.sql"
    
    if not init_sql_path.exists():
        raise FileNotFoundError(f"Le fichier init.sql n'a pas été trouvé à {init_sql_path}")
    
    # Exécution du script SQL
    system = platform.system().lower()
    if system == "windows":
        cmd = f"psql -U postgres -d auth_db -f {init_sql_path}"
    else:
        cmd = f"sudo -u postgres psql -d auth_db -f {init_sql_path}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Base de données initialisée avec succès")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise

def main():
    system = platform.system().lower()
    
    try:
        if system == "linux":
            install_postgres_linux()
        else:
            # Téléchargement de l'installeur
            installer_url = get_postgres_installer_url()
            if installer_url:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".exe" if system == "windows" else ".dmg") as tmp:
                    download_file(installer_url, tmp.name)
                    installer_path = tmp.name
                
                # Installation
                if system == "windows":
                    install_postgres_windows(installer_path)
                elif system == "darwin":
                    install_postgres_macos(installer_path)
                
                # Nettoyage
                os.unlink(installer_path)
        
        # Configuration
        configure_postgres()
        
        # Initialisation de la base de données
        initialize_database()
        
        print("Installation de PostgreSQL terminée avec succès")
        
    except Exception as e:
        print(f"Erreur lors de l'installation de PostgreSQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
