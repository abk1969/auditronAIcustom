"""Tests de sécurité pour XSS et CSRF."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_csrf_token

@pytest.mark.security
class TestXSSCSRFSecurity:
    def setup_method(self):
        self.client = TestClient(app)
        self.xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src='x' onerror='alert(1)'>",
            "<svg/onload=alert('xss')>",
            "'-alert(1)-'"
        ]

    async def test_xss_in_user_input(self):
        # Test XSS dans le profil utilisateur
        for payload in self.xss_payloads:
            response = await self.client.post(
                "/api/v1/users/profile",
                json={
                    "name": payload,
                    "bio": payload
                }
            )
            data = response.json()
            # Vérifier que les payloads sont échappés
            assert payload not in data["name"]
            assert payload not in data["bio"]
            assert "&lt;script&gt;" in data["name"] or payload not in data["name"]

    async def test_csrf_protection(self):
        # Test sans token CSRF
        response = await self.client.post("/api/v1/users/profile")
        assert response.status_code == 403

        # Test avec token CSRF invalide
        response = await self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRF-Token": "invalid"}
        )
        assert response.status_code == 403

        # Test avec token CSRF valide
        token = create_csrf_token()
        response = await self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRF-Token": token}
        )
        assert response.status_code != 403

    async def test_content_security_policy(self):
        response = await self.client.get("/")
        headers = response.headers
        assert "Content-Security-Policy" in headers
        csp = headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp 