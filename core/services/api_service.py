"""
Service for managing API configuration and validation
"""

import os
from typing import Optional, Dict, Any
from AuditronAI.core.logger import setup_logging

logger = setup_logging()

class APIService:
    """Service responsible for managing API configurations."""
    
    def __init__(self):
        """Initialize the API service."""
        self.required_apis = {
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
    
    def get_active_api(self) -> Optional[str]:
        """
        Get the currently active API service.
        
        Returns:
            Optional[str]: Name of active API service or None if none configured
        """
        return os.getenv('AI_SERVICE', 'openai')
    
    def get_api_key(self, service: Optional[str] = None) -> Optional[str]:
        """
        Get API key for specified service or active service.
        
        Args:
            service (Optional[str]): Service name or None for active service
            
        Returns:
            Optional[str]: API key if found, None otherwise
        """
        if not service:
            service = self.get_active_api()
            
        env_var = self.required_apis.get(service)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def is_configured(self) -> bool:
        """
        Check if any API service is properly configured.
        
        Returns:
            bool: True if at least one API is configured, False otherwise
        """
        return any(self.get_api_key(service) for service in self.required_apis)
    
    def get_configuration_status(self) -> Dict[str, bool]:
        """
        Get configuration status for all API services.
        
        Returns:
            Dict[str, bool]: Dictionary mapping service names to their configuration status
        """
        return {
            service: bool(self.get_api_key(service))
            for service in self.required_apis
        }
    
    def validate_api_key(self, api_key: str, service: str) -> bool:
        """
        Validate an API key for a specific service.
        
        Args:
            api_key (str): API key to validate
            service (str): Service name to validate for
            
        Returns:
            bool: True if key is valid, False otherwise
        """
        try:
            # Basic validation
            if not api_key or len(api_key) < 20:
                return False
                
            # Service-specific validation could be added here
            if service == 'openai' and not api_key.startswith('sk-'):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la clé API {service}: {str(e)}")
            return False
    
    def update_api_key(self, service: str, api_key: str) -> bool:
        """
        Update API key for a service.
        
        Args:
            service (str): Service name
            api_key (str): New API key
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if service not in self.required_apis:
                logger.error(f"Service API inconnu: {service}")
                return False
                
            if not self.validate_api_key(api_key, service):
                logger.error(f"Clé API invalide pour {service}")
                return False
                
            # Update environment variable
            os.environ[self.required_apis[service]] = api_key
            logger.info(f"Clé API mise à jour pour {service}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la clé API {service}: {str(e)}")
            return False
