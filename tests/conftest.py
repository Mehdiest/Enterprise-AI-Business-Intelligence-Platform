"""Shared pytest fixtures."""

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
# ایمپورت ماژول executor برای دستکاری SessionLocal درون آن
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
    engine = create_async_engine(_build_db_url(), pool_pre_ping=True)
    
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )

    # ذخیره حالت اصلی و جایگزینی آن در ماژول executor
    original_session_local = sql_executor_module.SessionLocal
    sql_executor_module.SessionLocal = TestingSessionLocal

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        
    await engine.dispose()
    
    # بازگرداندن حالت اصلی پس از پایان تست
    sql_executor_module.SessionLocal = original_session_local


@pytest_asyncio.fixture(scope="function")
async def client(db):
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
    response = await client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def authorized_client(client, access_token):
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest_asyncio.fixture
async def admin_user(db, client, test_user):
    await client.post("/auth/register", json=test_user)

    result = await db.execute(select(User).where(User.email == test_user["email"]))
    user = result.scalar_one_or_none()

    user.role = "admin"

    await db.commit()
    await db.refresh(user)

    return test_user


@pytest_asyncio.fixture
async def admin_access_token(client, admin_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    return response.json()["access_token"]


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