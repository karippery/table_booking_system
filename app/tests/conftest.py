# app/tests/conftest.py
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.main import app
from app.database import get_db
from app.tests.test_database import (
    TestingSessionLocal,
    init_test_db,
    drop_test_db,
    override_get_db
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    await drop_test_db()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    # Override the get_db dependency with our test session
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clear overrides after test
    app.dependency_overrides.clear()