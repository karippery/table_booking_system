# Run this in a Python shell or script after setting up your database
import os

from sqlalchemy import select
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from app.database import async_session


async def create_admin_user():
    async with async_session() as db:
        try:
            # Check if any admin exists
            result = await db.execute(
                select(User).where(User.role == UserRole.ADMIN)
            )
            admin_exists = result.scalars().first()

            if not admin_exists:
                admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
                admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

                admin_user = User(
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                    role=UserRole.ADMIN
                )
                db.add(admin_user)
                await db.commit()
                print("Initial admin user created")
            else:
                print("Admin user already exists")
        except Exception as e:
            print(f"Error creating initial admin: {str(e)}")
            await db.rollback()


create_admin_user()
