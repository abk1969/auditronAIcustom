"""Tests de smoke pour vérifier le déploiement."""
import requests
import sys
import time
from typing import Dict, List

class SmokeTests:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_user = {
            "email": "test@auditronai.com",
            "password": "test123"
        }
        self.access_token = None

    def run_all_tests(self) -> bool:
        tests = [
            self.test_backend_health,
            self.test_frontend_health,
            self.test_user_registration,
            self.test_user_login,
            self.test_protected_endpoints,
            self.test_database_connection,
            self.test_redis_connection
        ]

        success = True
        for test in tests:
            try:
                test()
                print(f"✅ {test.__name__} passed")
            except Exception as e:
                print(f"❌ {test.__name__} failed: {str(e)}")
                success = False

        return success

    def test_backend_health(self):
        response = requests.get(f"{self.backend_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_frontend_health(self):
        response = requests.get(self.frontend_url)
        assert response.status_code == 200

    def test_user_registration(self):
        response = requests.post(
            f"{self.backend_url}/api/v1/users/register",
            json=self.test_user
        )
        assert response.status_code in [201, 409]  # 409 si l'utilisateur existe déjà

    def test_user_login(self):
        response = requests.post(
            f"{self.backend_url}/api/v1/users/login",
            json=self.test_user
        )
        assert response.status_code == 200
        self.access_token = response.json()["access_token"]

    def test_protected_endpoints(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.backend_url}/api/v1/users/me",
            headers=headers
        )
        assert response.status_code == 200

    def test_database_connection(self):
        response = requests.get(f"{self.backend_url}/api/v1/health/db")
        assert response.status_code == 200
        assert response.json()["database"] == "connected"

    def test_redis_connection(self):
        response = requests.get(f"{self.backend_url}/api/v1/health/cache")
        assert response.status_code == 200
        assert response.json()["redis"] == "connected"

if __name__ == "__main__":
    print("Running smoke tests...")
    tests = SmokeTests()
    success = tests.run_all_tests()
    sys.exit(0 if success else 1) 