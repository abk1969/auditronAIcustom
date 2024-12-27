"""Tests de sécurité pour l'API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

@pytest.mark.security
class TestAPISecurity:
    def setup_method(self):
        self.client = TestClient(app)

    async def test_rate_limiting(self):
        # Tester la limite de requêtes
        for _ in range(100):
            response = await self.client.get("/api/v1/analyses")
        assert response.status_code == 429

    async def test_path_traversal(self):
        # Tester les tentatives de path traversal
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e%2f%2e%2e%2f",
            "....//....//",
        ]
        
        for path in dangerous_paths:
            response = await self.client.get(f"/api/v1/files/{path}")
            assert response.status_code in [400, 403, 404]
            assert "Access denied" in response.text

    async def test_secure_headers(self):
        response = await self.client.get("/")
        headers = response.headers
        
        # Vérifier les en-têtes de sécurité
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in headers

    async def test_sensitive_data_exposure(self):
        # Créer un utilisateur de test
        user_data = {
            "email": "test@example.com",
            "password": "secret123"
        }
        response = await self.client.post("/api/v1/users", json=user_data)
        
        # Vérifier que les données sensibles ne sont pas exposées
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "secret" not in str(data) 