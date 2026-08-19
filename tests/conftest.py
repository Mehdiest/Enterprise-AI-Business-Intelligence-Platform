"""Shared pytest fixtures for async database and client testing."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env.test")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.dependencies.rate_limit import _attempts
from app.main import app
from app.models.user import User
from app.monitoring import health as health_module
from app.services.ai.copilot.agents.sql import executor as sql_executor_module


def _build_db_url() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "test_db")
    user = os.getenv("POSTGRES_USER", "test")
    password = os.getenv("POSTGRES_PASSWORD", "test")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    _attempts.clear()
    yield
    _attempts.clear()


@pytest_asyncio.fixture(scope="function")
async def db():
    """Provide an isolated async database session."""
    test_engine = create_async_engine(_build_db_url(), pool_pre_ping=True)
    testing_session = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=test_engine,
    )

    orig_sql_exec = sql_executor_module.SessionLocal
    orig_health_engine = health_module.engine
    
    sql_executor_module.SessionLocal = testing_session
    health_module.engine = test_engine

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with testing_session() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()
    
    sql_executor_module.SessionLocal = orig_sql_exec
    health_module.engine = orig_health_engine


@pytest_asyncio.fixture(scope="function")
async def client(db):
    """Provide an async HTTP client with overridden dependencies."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    return {
        "full_name": "Mehdi Test",
        "email": "mehdi@test.com",
        "password": "StrongPass@123",
    }


@pytest_asyncio.fixture
async def registered_user(client, test_user):
    await client.post("/auth/register", json=test_user)
    return test_user


@pytest_asyncio.fixture
async def access_token(client, registered_user):
    res = await client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    return res.json()["access_token"]


@pytest_asyncio.fixture
async def authorized_client(client, access_token):
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest_asyncio.fixture
async def admin_user(db, client, test_user):
    await client.post("/auth/register", json=test_user)
    res = await db.execute(select(User).where(User.email == test_user["email"]))
    user = res.scalar_one_or_none()
    
    user.role = "admin"
    await db.commit()
    await db.refresh(user)
    
    return test_user


@pytest_asyncio.fixture
async def admin_access_token(client, admin_user):
    res = await client.post(
        "/auth/login",
        data={
            "username": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    return res.json()["access_token"]


@pytest_asyncio.fixture
async def admin_client(client, admin_access_token):
    client.headers.update({"Authorization": f"Bearer {admin_access_token}"})
    return client


@pytest.fixture
def sample_csv(tmp_path):
    file_path = tmp_path / "sales.csv"
    file_path.write_text(
        "customer_code,customer_name,product_code,product_name,region,channel,sale_date,quantity,amount\n"
        "C001,Alice,P001,Laptop,North,Online,2024-01-15,2,2400.00\n"
        "C002,Bob,P002,Phone,South,Retail,2024-01-16,1,800.00\n"
    )
    return file_path