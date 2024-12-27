"""Tests de sécurité pour l'authentification."""
import pytest
import jwt
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.core.security import get_password_hash
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.security
class TestAuthSecurity:
    async def test_password_hash_strength(self, auth_service, test_user):
        # Vérifier que le hash n'est pas réversible
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Les hashs doivent être différents (salt)
        assert hash1 != password  # Le hash ne doit pas être le mot de passe
        assert len(hash1) >= 60  # Longueur minimale pour bcrypt

    async def test_token_expiration(self, auth_service, test_user):
        # Créer un token expiré
        expire = datetime.utcnow() - timedelta(minutes=1)
        expired_token = jwt.encode(
            {"exp": expire, "sub": str(test_user.id)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Le token expiré ne doit pas être valide
        user = await auth_service.get_current_user(expired_token)
        assert user is None

    async def test_sql_injection_prevention(self, auth_service, mock_user_repository):
        # Tester avec des tentatives d'injection SQL
        injection_attempts = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users; --"
        ]
        
        for attempt in injection_attempts:
            user = await auth_service.authenticate_user(attempt, "password")
            assert user is None

    async def test_brute_force_protection(self, auth_service, redis_client):
        max_attempts = 5
        ip_address = "192.168.1.1"
        
        # Simuler plusieurs tentatives échouées
        for _ in range(max_attempts + 1):
            await auth_service.authenticate_user(
                "test@example.com", 
                "wrong_password",
                ip_address=ip_address
            )
        
        # Vérifier que le compte est temporairement bloqué
        is_blocked = await redis_client.get(f"login_attempts:{ip_address}")
        assert is_blocked is not None
        
        # Même avec le bon mot de passe, l'authentification doit échouer
        user = await auth_service.authenticate_user(
            "test@example.com",
            "correct_password",
            ip_address=ip_address
        )
        assert user is None 