"""Configuration des analyseurs de sécurité."""
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from ..logger import logger

@dataclass
class SecurityThresholds:
    """Seuils de sécurité pour l'analyse."""
    max_complexity: int = 10
    max_cognitive_complexity: int = 15
    max_line_length: int = 100
    max_function_length: int = 50
    min_test_coverage: float = 80.0
    max_vulnerabilities: Dict[str, int] = field(default_factory=lambda: {
        'critical': 0,
        'high': 0,
        'medium': 3,
        'low': 5
    })

@dataclass
class AnalyzerSettings:
    """Paramètres spécifiques pour chaque analyseur."""
    enabled: bool = True
    config_file: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

class AnalyzerConfig:
    """Configuration principale pour les analyseurs."""
    
    DEFAULT_CONFIG_PATH = "configs/analyzer_config.yaml"
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        env_prefix: str = "AUDITRON"
    ):
        """
        Initialise la configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            env_prefix: Préfixe pour les variables d'environnement
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.env_prefix = env_prefix
        self.thresholds = SecurityThresholds()
        self.analyzers: Dict[str, AnalyzerSettings] = {}
        self._load_config()

    @classmethod
    def from_env(cls) -> 'AnalyzerConfig':
        """
        Crée une configuration à partir des variables d'environnement.
        
        Returns:
            Instance de configuration
        """
        config_path = os.getenv('AUDITRON_CONFIG_PATH', cls.DEFAULT_CONFIG_PATH)
        return cls(config_path=config_path)

    def _load_config(self) -> None:
        """Charge la configuration depuis le fichier YAML et les variables d'environnement."""
        try:
            self._load_yaml_config()
            self._override_from_env()
            self._validate_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            self._load_default_config()

    def _load_yaml_config(self) -> None:
        """Charge la configuration depuis le fichier YAML."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    
                if config_data:
                    # Charger les seuils
                    if 'thresholds' in config_data:
                        for key, value in config_data['thresholds'].items():
                            if hasattr(self.thresholds, key):
                                setattr(self.thresholds, key, value)
                    
                    # Charger les configurations des analyseurs
                    if 'analyzers' in config_data:
                        for analyzer_name, settings in config_data['analyzers'].items():
                            self.analyzers[analyzer_name] = AnalyzerSettings(
                                enabled=settings.get('enabled', True),
                                config_file=settings.get('config_file'),
                                options=settings.get('options', {})
                            )
                            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier YAML: {str(e)}")
            raise

    def _override_from_env(self) -> None:
        """Surcharge la configuration avec les variables d'environnement."""
        # Format: AUDITRON_THRESHOLD_MAX_COMPLEXITY, AUDITRON_BANDIT_ENABLED, etc.
        for key, value in os.environ.items():
            if key.startswith(f"{self.env_prefix}_"):
                parts = key[len(self.env_prefix) + 1:].lower().split('_')
                
                if parts[0] == 'threshold':
                    attr_name = '_'.join(parts[1:])
                    if hasattr(self.thresholds, attr_name):
                        setattr(self.thresholds, attr_name, self._convert_value(value))
                        
                elif len(parts) >= 2:
                    analyzer_name = parts[0]
                    setting_name = '_'.join(parts[1:])
                    
                    if analyzer_name not in self.analyzers:
                        self.analyzers[analyzer_name] = AnalyzerSettings()
                    
                    if setting_name == 'enabled':
                        self.analyzers[analyzer_name].enabled = value.lower() == 'true'
                    elif setting_name == 'config_file':
                        self.analyzers[analyzer_name].config_file = value

    def _validate_config(self) -> None:
        """Valide la configuration."""
        # Vérifier les seuils
        if self.thresholds.max_complexity <= 0:
            raise ValueError("max_complexity doit être positif")
        if self.thresholds.max_cognitive_complexity <= 0:
            raise ValueError("max_cognitive_complexity doit être positif")
        if self.thresholds.max_line_length <= 0:
            raise ValueError("max_line_length doit être positif")
        if self.thresholds.min_test_coverage < 0 or self.thresholds.min_test_coverage > 100:
            raise ValueError("min_test_coverage doit être entre 0 et 100")
            
        # Vérifier les configurations des analyseurs
        for analyzer_name, settings in self.analyzers.items():
            if settings.config_file and not os.path.exists(settings.config_file):
                logger.warning(
                    f"Fichier de configuration non trouvé pour {analyzer_name}: {settings.config_file}"
                )

    def _load_default_config(self) -> None:
        """Charge la configuration par défaut."""
        self.thresholds = SecurityThresholds()
        self.analyzers = {
            'bandit': AnalyzerSettings(),
            'radon': AnalyzerSettings(),
            'vulture': AnalyzerSettings(),
            'prospector': AnalyzerSettings(),
            'typescript': AnalyzerSettings()
        }

    def _convert_value(self, value: str) -> Any:
        """
        Convertit une valeur de variable d'environnement.
        
        Args:
            value: Valeur à convertir
            
        Returns:
            Valeur convertie dans le type approprié
        """
        try:
            # Essayer de convertir en nombre
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # Gérer les booléens
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            # Retourner la chaîne si pas de conversion possible
            return value

    def get_analyzer_settings(self, analyzer_name: str) -> AnalyzerSettings:
        """
        Récupère les paramètres d'un analyseur.
        
        Args:
            analyzer_name: Nom de l'analyseur
            
        Returns:
            Paramètres de l'analyseur
        """
        return self.analyzers.get(analyzer_name, AnalyzerSettings())

    def is_analyzer_enabled(self, analyzer_name: str) -> bool:
        """
        Vérifie si un analyseur est activé.
        
        Args:
            analyzer_name: Nom de l'analyseur
            
        Returns:
            True si l'analyseur est activé
        """
        settings = self.get_analyzer_settings(analyzer_name)
        return settings.enabled

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la configuration en dictionnaire.
        
        Returns:
            Dict contenant la configuration
        """
        return {
            'thresholds': {
                key: getattr(self.thresholds, key)
                for key in self.thresholds.__annotations__
            },
            'analyzers': {
                name: {
                    'enabled': settings.enabled,
                    'config_file': settings.config_file,
                    'options': settings.options
                }
                for name, settings in self.analyzers.items()
            }
        }
