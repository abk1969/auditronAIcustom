"""Script de seed pour la base de données."""
from typing import List
import asyncio
from app.models.user import User
from app.models.analysis import Analysis
from app.core.security import get_password_hash
from app.db.session import async_session
from datetime import datetime, timedelta

async def create_test_users() -> List[User]:
    """Créer des utilisateurs de test."""
    users = [
        {
            "email": "admin@auditronai.com",
            "password": get_password_hash("admin123"),
            "is_admin": True
        },
        {
            "email": "user@auditronai.com",
            "password": get_password_hash("user123"),
            "is_admin": False
        }
    ]

    async with async_session() as session:
        db_users = []
        for user_data in users:
            user = User(**user_data)
            session.add(user)
            db_users.append(user)
        await session.commit()
        return db_users

async def create_test_analyses(users: List[User]):
    """Créer des analyses de test."""
    analyses = []
    for user in users:
        for i in range(5):
            analysis = {
                "user_id": user.id,
                "code_snippet": f"print('Test code {i}')",
                "language": "python",
                "status": "completed",
                "results": {"score": 85 + i, "issues": []},
                "created_at": datetime.utcnow() - timedelta(days=i)
            }
            analyses.append(analysis)

    async with async_session() as session:
        for analysis_data in analyses:
            analysis = Analysis(**analysis_data)
            session.add(analysis)
        await session.commit()

async def main():
    """Fonction principale de seed."""
    print("Starting database seed...")
    
    # Créer les utilisateurs
    users = await create_test_users()
    print("Created test users")
    
    # Créer les analyses
    await create_test_analyses(users)
    print("Created test analyses")
    
    print("Database seed completed!")

if __name__ == "__main__":
    asyncio.run(main()) 