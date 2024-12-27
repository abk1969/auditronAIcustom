"""Tests unitaires pour le service d'authentification."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

@pytest.fixture
def mock_user_repository():
    return Mock()

@pytest.fixture
def auth_service(mock_user_repository):
    return AuthService(repository=mock_user_repository)

@pytest.fixture
def test_user():
    user = User(
        email="test@example.com",
        username="testuser",
        role=UserRole.USER
    )
    user.set_password("testpassword")
    return user

class TestAuthService:
    async def test_authenticate_user_success(self, auth_service, mock_user_repository, test_user):
        mock_user_repository.get_by_email.return_value = test_user
        user = await auth_service.authenticate_user("test@example.com", "testpassword")
        assert user == test_user

    async def test_authenticate_user_invalid_password(self, auth_service, mock_user_repository, test_user):
        mock_user_repository.get_by_email.return_value = test_user
        user = await auth_service.authenticate_user("test@example.com", "wrongpassword")
        assert user is None

    def test_create_access_token(self, auth_service):
        token = auth_service.create_access_token("user_id")
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_get_current_user_success(self, auth_service, mock_user_repository, test_user):
        mock_user_repository.get.return_value = test_user
        token = auth_service.create_access_token(str(test_user.id))
        user = await auth_service.get_current_user(token)
        assert user == test_user 