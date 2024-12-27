"""Scripts de déploiement pour AuditronAI."""
import subprocess
import os
from pathlib import Path
import yaml
import shutil
from typing import Dict, Any
import time

from ..core.logger import logger

class Deployer:
    """Gestionnaire de déploiement."""
    
    def __init__(self, config_file: str = "deploy/config.yaml"):
        """
        Initialise le déploiement.
        
        Args:
            config_file: Fichier de configuration
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration de déploiement."""
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(f"Configuration non trouvée: {self.config_file}")
                
            with open(self.config_file) as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return {}
    
    def deploy(self, environment: str = "production"):
        """
        Déploie l'application.
        
        Args:
            environment: Environnement cible
        """
        try:
            if environment not in self.config:
                raise ValueError(f"Environnement inconnu: {environment}")
            
            env_config = self.config[environment]
            
            # Vérifier les prérequis
            self._check_prerequisites(env_config)
            
            # Construire l'image Docker
            self._build_docker_image(env_config)
            
            # Déployer les services
            self._deploy_services(env_config)
            
            # Vérifier le déploiement
            self._verify_deployment(env_config)
            
            logger.info(f"Déploiement réussi sur {environment}")
            
        except Exception as e:
            logger.error(f"Erreur lors du déploiement: {e}")
            raise
    
    def _check_prerequisites(self, config: Dict[str, Any]):
        """Vérifie les prérequis."""
        required_commands = ['docker', 'docker-compose', 'kubectl']
        
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                raise RuntimeError(f"Commande requise non trouvée: {cmd}")
    
    def _build_docker_image(self, config: Dict[str, Any]):
        """Construit l'image Docker."""
        try:
            subprocess.run([
                'docker', 'build',
                '-t', config['image'],
                '-f', 'Dockerfile',
                '.'
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la construction de l'image: {e}")
    
    def _deploy_services(self, config: Dict[str, Any]):
        """Déploie les services."""
        try:
            if config.get('use_kubernetes'):
                self._deploy_kubernetes(config)
            else:
                self._deploy_docker_compose(config)
        except Exception as e:
            raise RuntimeError(f"Erreur lors du déploiement des services: {e}")
    
    def _deploy_kubernetes(self, config: Dict[str, Any]):
        """Déploie sur Kubernetes."""
        try:
            # Appliquer les configurations
            for manifest in Path('deploy/kubernetes').glob('*.yaml'):
                subprocess.run([
                    'kubectl', 'apply',
                    '-f', str(manifest)
                ], check=True)
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors du déploiement Kubernetes: {e}")
    
    def _deploy_docker_compose(self, config: Dict[str, Any]):
        """Déploie avec Docker Compose."""
        try:
            subprocess.run([
                'docker-compose',
                '-f', 'docker-compose.yml',
                'up', '-d'
            ], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors du déploiement Docker Compose: {e}")
    
    def _verify_deployment(self, config: Dict[str, Any]):
        """Vérifie le déploiement."""
        max_retries = 5
        retry_delay = 10
        
        for i in range(max_retries):
            try:
                # Vérifier les services
                if config.get('use_kubernetes'):
                    subprocess.run([
                        'kubectl', 'get', 'pods',
                        '--field-selector', 'status.phase=Running'
                    ], check=True)
                else:
                    subprocess.run([
                        'docker-compose',
                        'ps', '--filter', 'status=running'
                    ], check=True)
                
                return
                
            except subprocess.CalledProcessError:
                if i < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError("Échec de la vérification du déploiement") 