"""Script d'initialisation de la base de données."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import db
from app.models.user import User, Role
from app.core.logging import get_logger

logger = get_logger(__name__)

async def init_db() -> None:
    """Initialise la base de données."""
    try:
        # Crée les tables
        async with db.engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)
        
        # Crée un utilisateur par défaut
        async with AsyncSession(db.engine) as session:
            # Vérifie si l'utilisateur existe déjà
            user = await session.query(User).filter(User.email == "admin@auditronai.com").first()
            if not user:
                # Crée le rôle admin
                admin_role = Role(
                    name="admin",
                    description="Administrateur système",
                    permissions=["*"]
                )
                session.add(admin_role)
                await session.flush()
                
                # Crée l'utilisateur admin
                admin = User(
                    email="admin@auditronai.com",
                    username="admin",
                    full_name="Admin",
                    password="admin123",  # À changer en production !
                    is_superuser=True,
                    is_verified=True
                )
                admin.roles.append(admin_role)
                session.add(admin)
                
                await session.commit()
                logger.info("Utilisateur admin créé avec succès")
            else:
                logger.info("L'utilisateur admin existe déjà")
                
    except Exception as e:
        logger.error(
            "Erreur lors de l'initialisation de la base de données",
            extra={"error": str(e)},
            exc_info=True
        )
        raise

if __name__ == "__main__":
    asyncio.run(init_db()) 