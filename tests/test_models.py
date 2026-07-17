"""Tests for SQLAlchemy models."""

from __future__ import annotations

from app.models.user import User
from app.models.warehouse import DimCustomer, DimProduct, DimRegion, FactSales


def test_user_model_fields():
    assert hasattr(User, "id")
    assert hasattr(User, "email")
    assert hasattr(User, "full_name")
    assert hasattr(User, "hashed_password")
    assert hasattr(User, "role")
    assert hasattr(User, "is_active")


def test_user_default_role(db):
    user = User(
        full_name="Test",
        email="test@model.com",
        hashed_password="hashed",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.role == "viewer"
    assert user.is_active is True


def test_dim_customer_exists():
    assert hasattr(DimCustomer, "__tablename__")


def test_dim_product_exists():
    assert hasattr(DimProduct, "__tablename__")


def test_dim_region_exists():
    assert hasattr(DimRegion, "__tablename__")


def test_fact_sales_exists():
    assert hasattr(FactSales, "__tablename__")
