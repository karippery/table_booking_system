import os
import asyncio
from sqlalchemy import select
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from app.database import async_session


async def create_admin_user():
    """Create initial admin user if none exists"""
    async with async_session() as db:
        try:
            # Check if any admin exists
            result = await db.execute(
                select(User).where(User.role == UserRole.ADMIN)
            )
            admin_exists = result.scalars().first()
            if not admin_exists:
                admin_email = os.getenv(
                    "INITIAL_ADMIN_EMAIL", "admin@example.com"
                    )
                admin_password = os.getenv(
                    "INITIAL_ADMIN_PASSWORD", "Admin@1234"
                    )

                if not admin_email or not admin_password:
                    raise ValueError(
                        "Admin email and password must be set in environment"
                        )

                admin_user = User(
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                    role=UserRole.ADMIN
                )
                db.add(admin_user)
                await db.commit()
                print("Initial admin user created")
                return True
            print(" Admin user already exists")
            return False
        except Exception as e:
            print(f"Error creating initial admin: {str(e)}")
            await db.rollback()
            raise

# Only run directly when executed as a script
if __name__ == "__main__":
    asyncio.run(create_admin_user())
