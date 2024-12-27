"""Gestionnaire d'autorisation RBAC pour AuditronAI."""

from enum import Enum
from typing import Dict, List, Optional, Set
from fastapi import HTTPException
from pydantic import BaseModel

from .security_auditor import security_auditor

class Permission(str, Enum):
    """Permissions disponibles."""
    
    # Permissions globales
    ADMIN = "admin"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # Permissions spécifiques
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_ROLES = "manage_roles"
    MANAGE_SETTINGS = "manage_settings"
    RUN_ANALYSIS = "run_analysis"
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"
    MANAGE_PLUGINS = "manage_plugins"

class Role(BaseModel):
    """Modèle pour un rôle."""
    
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[str] = None

class RBACManager:
    """Gestionnaire d'autorisation RBAC."""

    def __init__(self) -> None:
        """Initialise le gestionnaire RBAC."""
        self._roles: Dict[str, Role] = {}
        self._setup_default_roles()

    def _setup_default_roles(self) -> None:
        """Configure les rôles par défaut."""
        # Rôle administrateur
        self.add_role(
            name="admin",
            description="Administrateur système avec tous les droits",
            permissions=set(Permission)
        )
        
        # Rôle analyste
        self.add_role(
            name="analyst",
            description="Analyste avec accès aux fonctionnalités d'analyse",
            permissions={
                Permission.READ,
                Permission.RUN_ANALYSIS,
                Permission.VIEW_REPORTS,
                Permission.EXPORT_DATA
            }
        )
        
        # Rôle auditeur
        self.add_role(
            name="auditor",
            description="Auditeur avec accès en lecture seule",
            permissions={
                Permission.READ,
                Permission.VIEW_AUDIT_LOGS,
                Permission.VIEW_REPORTS
            }
        )
        
        # Rôle utilisateur
        self.add_role(
            name="user",
            description="Utilisateur standard",
            permissions={
                Permission.READ,
                Permission.RUN_ANALYSIS
            }
        )

    def add_role(
        self,
        name: str,
        description: str,
        permissions: Set[Permission],
        inherits_from: Optional[str] = None
    ) -> None:
        """Ajoute un nouveau rôle.
        
        Args:
            name: Nom du rôle
            description: Description du rôle
            permissions: Permissions du rôle
            inherits_from: Rôle dont hériter les permissions
            
        Raises:
            ValueError: Si le rôle existe déjà ou si le rôle parent n'existe pas
        """
        if name in self._roles:
            raise ValueError(f"Le rôle {name} existe déjà")
            
        if inherits_from and inherits_from not in self._roles:
            raise ValueError(
                f"Le rôle parent {inherits_from} n'existe pas"
            )
            
        # Combine les permissions héritées
        if inherits_from:
            parent_role = self._roles[inherits_from]
            permissions = permissions.union(parent_role.permissions)
            
        self._roles[name] = Role(
            name=name,
            description=description,
            permissions=permissions,
            inherits_from=inherits_from
        )
        
        security_auditor.log_security_event(
            event_type="role_created",
            description=f"Nouveau rôle créé: {name}",
            severity="INFO",
            details={
                "role_name": name,
                "permissions": list(permissions)
            }
        )

    def remove_role(self, name: str) -> None:
        """Supprime un rôle.
        
        Args:
            name: Nom du rôle à supprimer
            
        Raises:
            ValueError: Si le rôle n'existe pas ou est utilisé comme parent
        """
        if name not in self._roles:
            raise ValueError(f"Le rôle {name} n'existe pas")
            
        # Vérifie si le rôle est utilisé comme parent
        for role in self._roles.values():
            if role.inherits_from == name:
                raise ValueError(
                    f"Le rôle {name} est utilisé comme parent"
                )
                
        del self._roles[name]
        
        security_auditor.log_security_event(
            event_type="role_deleted",
            description=f"Rôle supprimé: {name}",
            severity="WARNING"
        )

    def get_role_permissions(self, role_name: str) -> Set[Permission]:
        """Récupère les permissions d'un rôle.
        
        Args:
            role_name: Nom du rôle
            
        Returns:
            Ensemble des permissions
            
        Raises:
            ValueError: Si le rôle n'existe pas
        """
        if role_name not in self._roles:
            raise ValueError(f"Le rôle {role_name} n'existe pas")
            
        return self._roles[role_name].permissions

    def has_permission(
        self,
        user_roles: List[str],
        required_permission: Permission
    ) -> bool:
        """Vérifie si l'utilisateur a une permission.
        
        Args:
            user_roles: Rôles de l'utilisateur
            required_permission: Permission requise
            
        Returns:
            True si l'utilisateur a la permission
        """
        for role_name in user_roles:
            if role_name not in self._roles:
                continue
                
            role = self._roles[role_name]
            if required_permission in role.permissions:
                return True
                
        return False

    def check_permission(
        self,
        user_roles: List[str],
        required_permission: Permission,
        raise_error: bool = True
    ) -> bool:
        """Vérifie si l'utilisateur a une permission et lève une exception si nécessaire.
        
        Args:
            user_roles: Rôles de l'utilisateur
            required_permission: Permission requise
            raise_error: Si True, lève une exception si la permission est manquante
            
        Returns:
            True si l'utilisateur a la permission
            
        Raises:
            HTTPException: Si l'utilisateur n'a pas la permission et raise_error est True
        """
        has_perm = self.has_permission(user_roles, required_permission)
        
        if not has_perm and raise_error:
            security_auditor.log_security_event(
                event_type="permission_denied",
                description="Tentative d'accès non autorisé",
                severity="WARNING",
                details={
                    "roles": user_roles,
                    "required_permission": required_permission
                }
            )
            
            raise HTTPException(
                status_code=403,
                detail="Permission insuffisante"
            )
            
        return has_perm

    def update_role_permissions(
        self,
        role_name: str,
        permissions: Set[Permission]
    ) -> None:
        """Met à jour les permissions d'un rôle.
        
        Args:
            role_name: Nom du rôle
            permissions: Nouvelles permissions
            
        Raises:
            ValueError: Si le rôle n'existe pas
        """
        if role_name not in self._roles:
            raise ValueError(f"Le rôle {role_name} n'existe pas")
            
        old_permissions = self._roles[role_name].permissions
        self._roles[role_name].permissions = permissions
        
        security_auditor.log_security_event(
            event_type="role_updated",
            description=f"Permissions du rôle {role_name} mises à jour",
            severity="INFO",
            details={
                "role_name": role_name,
                "old_permissions": list(old_permissions),
                "new_permissions": list(permissions)
            }
        )

# Instance globale du gestionnaire RBAC
rbac_manager = RBACManager() 