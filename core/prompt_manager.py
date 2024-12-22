"""Gestionnaire de prompts pour AuditronAI."""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import logger

class PromptManager:
    """Gère les prompts et leur configuration."""
    
    def __init__(self, template_path: Optional[str] = None):
        """
        Initialise le gestionnaire de prompts.
        
        Args:
            template_path: Chemin vers le fichier de templates (optionnel)
        
        Raises:
            FileNotFoundError: Si le fichier de templates n'existe pas
            yaml.YAMLError: Si le fichier YAML est invalide
        """
        if template_path is None:
            template_path = Path(__file__).parent.parent / "templates" / "prompts.yaml"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.templates = yaml.safe_load(f)
                logger.info(f"Templates chargés depuis {template_path}")
                
            self.default_config = self.templates.get('default', {})
            if not self.default_config:
                logger.warning("Configuration par défaut manquante")
                
        except FileNotFoundError:
            error_msg = f"Fichier de templates non trouvé : {template_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        except yaml.YAMLError as e:
            error_msg = f"Erreur de parsing YAML : {str(e)}"
            logger.error(error_msg)
            raise
    
    def get_prompt(self, prompt_name: str, **kwargs) -> Dict[str, Any]:
        """
        Récupère un prompt configuré.
        
        Args:
            prompt_name: Nom du prompt à récupérer
            **kwargs: Variables pour formater le prompt
            
        Returns:
            Dict[str, Any]: Configuration du prompt
            
        Raises:
            ValueError: Si le prompt n'existe pas
            KeyError: Si des variables requises sont manquantes
        """
        if prompt_name not in self.templates.get('custom_prompts', {}):
            error_msg = f"Prompt '{prompt_name}' non trouvé"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            prompt_config = self.templates['custom_prompts'][prompt_name].copy()
            
            # Formatter le prompt avec les variables fournies
            if 'user' in prompt_config:
                prompt_config['user'] = prompt_config['user'].format(**kwargs)
                
            # Fusionner avec les paramètres par défaut
            config = {**self.default_config, **prompt_config}
            logger.debug(f"Prompt '{prompt_name}' configuré avec succès")
            return config
            
        except KeyError as e:
            error_msg = f"Variable manquante pour le prompt '{prompt_name}': {str(e)}"
            logger.error(error_msg)
            raise KeyError(error_msg)