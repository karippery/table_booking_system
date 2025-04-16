# crud/user.py
from typing import List, Optional
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.deps.pagination import PaginationParams
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash

# This module contains CRUD operations for the User model.


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        role=UserRole.GUEST,

    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession,
    db_user: User,
    user_update: UserUpdate
) -> User:
    """Update user information."""
    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]

    await db.execute(
        update(User)
        .where(User.id == db_user.id)
        .values(**update_data)
    )
    await db.commit()

    # Refresh and return updated user
    return await get_user(db, db_user.id)


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_users(
    db: AsyncSession, 
    pagination: PaginationParams,
    filters: Optional[dict] = None
) -> List[User]:
    """Get paginated list of users with optional filtering."""
    query = select(User).offset(
        (pagination["page"] - 1) * pagination["size"]
    ).limit(pagination["size"])

    if filters:
        for field, value in filters.items():
            query = query.where(getattr(User, field) == value)

    result = await db.execute(query)
    return result.scalars().all()


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete a user."""
    result = await db.execute(
        delete(User).where(User.id == user_id)
    )
    await db.commit()
    return result.rowcount > 0
