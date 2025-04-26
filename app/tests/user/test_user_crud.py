# tests/user/test_user_crud.py
import pytest
from app.crud import user as user_crud
from app.schemas.user import UserCreate
from app.utils.security import verify_password


@pytest.mark.asyncio
async def test_create_and_get_user(db_session):
    new_user = UserCreate(email="test@example.com", password="StrongPass123")
    user = await user_crud.create_user(db_session, user=new_user)

    assert user.email == "test@example.com"
    assert user.is_active
    assert user.role == "guest"
    assert verify_password("StrongPass123", user.hashed_password)

    user_fetched = await user_crud.get_user(db_session, user.id)
    assert user_fetched.email == "test@example.com"