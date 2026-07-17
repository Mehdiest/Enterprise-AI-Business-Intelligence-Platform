"""Shared pytest fixtures."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.dependencies.rate_limit import _attempts
from app.main import app
from app.models.user import User


def _build_db_url() ->str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "test_db")
    user = os.getenv("POSTGRES_USER", "test")
    password = os.getenv("POSTGRES_PASSWORD", "test")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


engine = create_engine(
    _build_db_url(),
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    _attempts.clear()
    yield
    _attempts.clear()


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    return {
        "full_name": "Mehdi Test",
        "email": "mehdi@test.com",
        "password": "StrongPass@123",
    }


@pytest.fixture
def registered_user(client, test_user):
    client.post("/auth/register", json=test_user)
    return test_user


@pytest.fixture
def access_token(client, registered_user):
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def authorized_client(client, access_token):
    client.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
        }
    )
    return client


# ------------------------------------------------------------------
# Admin Fixtures (RBAC Tests)
# ------------------------------------------------------------------

@pytest.fixture
def admin_user(db, client, test_user):
    client.post("/auth/register", json=test_user)

    user = (
        db.query(User)
        .filter(User.email == test_user["email"])
        .first()
    )

    user.role = "admin"

    db.commit()
    db.refresh(user)

    return test_user


@pytest.fixture
def admin_access_token(client, admin_user):
    response = client.post(
        "/auth/login",
        data={
            "username": admin_user["email"],
            "password": admin_user["password"],
        },
    )

    return response.json()["access_token"]


@pytest.fixture
def admin_client(client, admin_access_token):
    client.headers.update(
        {
            "Authorization": f"Bearer {admin_access_token}",
        }
    )

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