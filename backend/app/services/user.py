"""Service utilisateur."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt

from app.core.config import settings
from app.core.security.password import get_password_hash, verify_password
from app.core.security.token import create_token, decode_token
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService
from app.core.exceptions import (
    CredentialsException,
    NotFoundException,
    ValidationException
)
from app.core.logging import get_logger

logger = get_logger(__name__)

class UserService(BaseService[User, UserCreate, UserUpdate]):
    """Service de gestion des utilisateurs."""
    
    def __init__(self):
        """Initialise le service."""
        super().__init__(User, UserCreate, UserUpdate)
    
    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authentifie un utilisateur.
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe
            
        Returns:
            Utilisateur authentifié
            
        Raises:
            CredentialsException: Si l'authentification échoue
        """
        try:
            user = await self.get_by_email(db, email=email)
            if not user:
                raise CredentialsException("Email ou mot de passe incorrect")
                
            if not verify_password(password, user.hashed_password):
                raise CredentialsException("Email ou mot de passe incorrect")
                
            if not user.is_active:
                raise CredentialsException("Compte désactivé")
                
            return user
            
        except Exception as e:
            logger.error(
                "Erreur lors de l'authentification",
                extra={"email": email, "error": str(e)}
            )
            raise
    
    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: str
    ) -> Optional[User]:
        """Récupère un utilisateur par son email.
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            
        Returns:
            Utilisateur trouvé
        """
        try:
            query = select(User).where(User.email == email)
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Erreur lors de la récupération par email",
                extra={"email": email, "error": str(e)}
            )
            raise
    
    async def create_with_role(
        self,
        db: AsyncSession,
        *,
        obj_in: UserCreate,
        role_name: str = "user"
    ) -> User:
        """Crée un utilisateur avec un rôle.
        
        Args:
            db: Session de base de données
            obj_in: Données de l'utilisateur
            role_name: Nom du rôle
            
        Returns:
            Utilisateur créé
            
        Raises:
            ValidationException: Si l'email existe déjà
        """
        try:
            # Vérifie si l'email existe
            if await self.get_by_email(db, email=obj_in.email):
                raise ValidationException("Email déjà utilisé")
            
            # Récupère le rôle
            query = select(Role).where(Role.name == role_name)
            result = await db.execute(query)
            role = result.scalar_one_or_none()
            
            if not role:
                # Crée le rôle s'il n'existe pas
                role = Role(
                    name=role_name,
                    description=f"Rôle {role_name}",
                    permissions=[f"{role_name}.*"]
                )
                db.add(role)
                
            # Crée l'utilisateur
            user = await super().create(db, obj_in=obj_in)
            
            # Ajoute le rôle
            user.roles.append(role)
            await db.commit()
            await db.refresh(user)
            
            return user
            
        except Exception as e:
            logger.error(
                "Erreur lors de la création avec rôle",
                extra={
                    "email": obj_in.email,
                    "role": role_name,
                    "error": str(e)
                }
            )
            raise
    
    async def change_password(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> User:
        """Change le mot de passe d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            Utilisateur mis à jour
            
        Raises:
            CredentialsException: Si le mot de passe actuel est incorrect
            NotFoundException: Si l'utilisateur n'existe pas
        """
        try:
            user = await self.get(db, id=user_id)
            if not user:
                raise NotFoundException("Utilisateur non trouvé")
                
            if not verify_password(current_password, user.hashed_password):
                raise CredentialsException("Mot de passe actuel incorrect")
                
            hashed_password = get_password_hash(new_password)
            return await self.update(
                db,
                db_obj=user,
                obj_in={"hashed_password": hashed_password}
            )
            
        except Exception as e:
            logger.error(
                "Erreur lors du changement de mot de passe",
                extra={"user_id": str(user_id), "error": str(e)}
            )
            raise
    
    async def request_password_reset(
        self,
        db: AsyncSession,
        *,
        email: str
    ) -> Optional[str]:
        """Demande une réinitialisation de mot de passe.
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            
        Returns:
            Token de réinitialisation
        """
        try:
            user = await self.get_by_email(db, email=email)
            if not user:
                return None
                
            # Génère un token
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(
                hours=settings.RESET_TOKEN_EXPIRE_HOURS
            )
            
            # Met à jour l'utilisateur
            user.reset_token = create_token(
                {"sub": str(user.id), "exp": expires.timestamp()},
                token
            )
            db.add(user)
            await db.commit()
            
            return token
            
        except Exception as e:
            logger.error(
                "Erreur lors de la demande de réinitialisation",
                extra={"email": email, "error": str(e)}
            )
            raise
    
    async def reset_password(
        self,
        db: AsyncSession,
        *,
        token: str,
        new_password: str
    ) -> Optional[User]:
        """Réinitialise le mot de passe d'un utilisateur.
        
        Args:
            db: Session de base de données
            token: Token de réinitialisation
            new_password: Nouveau mot de passe
            
        Returns:
            Utilisateur mis à jour
            
        Raises:
            CredentialsException: Si le token est invalide
        """
        try:
            # Décode le token
            payload = decode_token(token)
            if not payload:
                raise CredentialsException("Token invalide")
                
            # Récupère l'utilisateur
            user = await self.get(db, id=UUID(payload["sub"]))
            if not user or not user.reset_token:
                raise CredentialsException("Token invalide")
                
            # Vérifie le token
            if user.reset_token != token:
                raise CredentialsException("Token invalide")
                
            # Met à jour le mot de passe
            hashed_password = get_password_hash(new_password)
            user.hashed_password = hashed_password
            user.reset_token = None
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            return user
            
        except Exception as e:
            logger.error(
                "Erreur lors de la réinitialisation du mot de passe",
                extra={"error": str(e)}
            )
            raise
    
    async def verify_email(
        self,
        db: AsyncSession,
        *,
        token: str
    ) -> Optional[User]:
        """Vérifie l'email d'un utilisateur.
        
        Args:
            db: Session de base de données
            token: Token de vérification
            
        Returns:
            Utilisateur vérifié
            
        Raises:
            CredentialsException: Si le token est invalide
        """
        try:
            # Décode le token
            payload = decode_token(token)
            if not payload:
                raise CredentialsException("Token invalide")
                
            # Récupère l'utilisateur
            user = await self.get(db, id=UUID(payload["sub"]))
            if not user or not user.verification_token:
                raise CredentialsException("Token invalide")
                
            # Vérifie le token
            if user.verification_token != token:
                raise CredentialsException("Token invalide")
                
            # Met à jour l'utilisateur
            user.is_verified = True
            user.verification_token = None
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            return user
            
        except Exception as e:
            logger.error(
                "Erreur lors de la vérification de l'email",
                extra={"error": str(e)}
            )
            raise
    
    async def generate_verification_token(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> Optional[str]:
        """Génère un token de vérification.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Token de vérification
            
        Raises:
            NotFoundException: Si l'utilisateur n'existe pas
        """
        try:
            user = await self.get(db, id=user_id)
            if not user:
                raise NotFoundException("Utilisateur non trouvé")
                
            # Génère un token
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(
                hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS
            )
            
            # Met à jour l'utilisateur
            user.verification_token = create_token(
                {"sub": str(user.id), "exp": expires.timestamp()},
                token
            )
            db.add(user)
            await db.commit()
            
            return token
            
        except Exception as e:
            logger.error(
                "Erreur lors de la génération du token de vérification",
                extra={"user_id": str(user_id), "error": str(e)}
            )
            raise
    
    async def generate_mfa_secret(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> Tuple[str, List[str]]:
        """Génère un secret MFA.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            Tuple (secret, codes de secours)
            
        Raises:
            NotFoundException: Si l'utilisateur n'existe pas
        """
        try:
            user = await self.get(db, id=user_id)
            if not user:
                raise NotFoundException("Utilisateur non trouvé")
                
            # Génère un secret
            secret = secrets.token_hex(20)
            
            # Génère des codes de secours
            backup_codes = [secrets.token_hex(4) for _ in range(8)]
            
            # Met à jour l'utilisateur
            user.mfa_secret = secret
            user.backup_codes = backup_codes
            db.add(user)
            await db.commit()
            
            return secret, backup_codes
            
        except Exception as e:
            logger.error(
                "Erreur lors de la génération du secret MFA",
                extra={"user_id": str(user_id), "error": str(e)}
            )
            raise
    
    async def verify_mfa_code(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        code: str
    ) -> bool:
        """Vérifie un code MFA.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            code: Code MFA
            
        Returns:
            True si le code est valide
            
        Raises:
            NotFoundException: Si l'utilisateur n'existe pas
        """
        try:
            user = await self.get(db, id=user_id)
            if not user:
                raise NotFoundException("Utilisateur non trouvé")
                
            if not user.mfa_enabled or not user.mfa_secret:
                return False
                
            # Vérifie le code
            if code in user.backup_codes:
                # Supprime le code de secours utilisé
                user.backup_codes.remove(code)
                db.add(user)
                await db.commit()
                return True
                
            # TODO: Implémenter la vérification TOTP
            return False
            
        except Exception as e:
            logger.error(
                "Erreur lors de la vérification du code MFA",
                extra={"user_id": str(user_id), "error": str(e)}
            )
            raise 